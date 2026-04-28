#region imports
import math

from PyQt5 import QtCore as qtc
from PyQt5 import QtGui as qtg
from PyQt5 import QtWidgets as qtw

from GraphicsView_App import RigidLink, RigidPivotPoint
#endregion


#region constants
DEFAULT_LINK_MATERIAL = "steel"
DEFAULT_LINK_THICKNESS_IN = 0.25
DEFAULT_LINK_WIDTH_IN = 2.00
DENSITY_LB_PER_IN3 = {
    "steel": 0.284,
    "aluminum": 0.098,
}
#endregion


#region graphics item definitions
class TrussLinkItem(RigidLink):
    # Chat GPT helped me write this function.
    def __init__(
        self,
        start_x,
        start_y,
        end_x,
        end_y,
        radius=10,
        parent=None,
        pen=None,
        brush=None,
        name="TrussLinkItem",
        tooltip_text="",
    ):
        """
        Create a link drawing item that keeps the truss-specific tooltip text.

        Args:
            start_x: Scene x-coordinate for the first link endpoint.
            start_y: Scene y-coordinate for the first link endpoint.
            end_x: Scene x-coordinate for the second link endpoint.
            end_y: Scene y-coordinate for the second link endpoint.
            radius: Half-thickness used when drawing the link.
            parent: Optional parent QGraphicsItem.
            pen: Pen used to outline the link.
            brush: Brush used to fill the link.
            name: Short item name shown in the mouse tracker.
            tooltip_text: Full tooltip text shown when hovering over the link.

        Returns:
            None.
        """
        super().__init__(
            start_x,
            start_y,
            end_x,
            end_y,
            radius=radius,
            parent=parent,
            pen=pen,
            brush=brush,
            name=name,
        )
        self.tooltip_text = tooltip_text
        self.setData(0, name)
        self.setToolTip(tooltip_text)

    # Chat GPT helped me write this function.
    def paint(self, painter, option, widget=None):
        """
        Draw the inherited rigid link and then restore the detailed tooltip.

        Args:
            painter: Qt painter used by the scene.
            option: Qt style option for the graphics item.
            widget: Optional widget being painted.

        Returns:
            None.
        """
        super().paint(painter, option, widget)
        self.setToolTip(self.tooltip_text)


class RollerSupport(qtw.QGraphicsItem):
    # Chat GPT helped me write this function.
    def __init__(
        self,
        point_x,
        point_y,
        pivot_height,
        pivot_width,
        parent=None,
        pen=None,
        brush=None,
        rotation=0,
        name="RollerSupport",
        tooltip_text="",
    ):
        """
        Create a roller support graphics item for the right truss support.

        Args:
            point_x: Scene x-coordinate of the supported node.
            point_y: Scene y-coordinate of the supported node.
            pivot_height: Height of the triangular support body.
            pivot_width: Width of the triangular support body.
            parent: Optional parent QGraphicsItem.
            pen: Pen used to outline the roller.
            brush: Brush used to fill the support.
            rotation: Rotation angle for the support in degrees.
            name: Short item name shown in the mouse tracker.
            tooltip_text: Full tooltip text shown when hovering over the node.

        Returns:
            None.
        """
        super().__init__(parent)
        self.x = point_x
        self.y = point_y
        self.height = pivot_height
        self.width = pivot_width
        self.pen = pen
        self.brush = brush
        self.rotation_angle = rotation
        self.name = name
        self.tooltip_text = tooltip_text
        self.transformation = qtg.QTransform()
        self.roller_radius = min(self.height, self.width) / 6.0
        self.rect = qtc.QRectF(
            -self.width,
            -self.roller_radius,
            2.0 * self.width,
            self.height + 5.0 * self.roller_radius,
        )
        self.setData(0, name)
        self.setToolTip(tooltip_text)

    # Chat GPT helped me write this function.
    def boundingRect(self):
        """
        Return the roller support bounding rectangle in scene coordinates.

        Args:
            None.

        Returns:
            Qt rectangle containing the transformed roller support.
        """
        return self.transformation.mapRect(self.rect)

    # Chat GPT helped me write this function.
    def paint(self, painter, option, widget=None):
        """
        Draw the roller support triangle, rollers, and ground line.

        Args:
            painter: Qt painter used by the scene.
            option: Qt style option for the graphics item.
            widget: Optional widget being painted.

        Returns:
            None.
        """
        support_path = qtg.QPainterPath()
        support_path.moveTo(0.0, 0.0)
        support_path.lineTo(self.width / 2.0, self.height)
        support_path.lineTo(-self.width / 2.0, self.height)
        support_path.closeSubpath()

        if self.pen is not None:
            painter.setPen(self.pen)
        if self.brush is not None:
            painter.setBrush(self.brush)

        painter.drawPath(support_path)

        # Draw a small pivot circle at the node.
        pivot_radius = min(self.height, self.width) / 2.0
        pivot_rect = qtc.QRectF(-pivot_radius, -pivot_radius, 2.0 * pivot_radius, 2.0 * pivot_radius)
        painter.drawEllipse(pivot_rect)

        # Draw two rollers under the support body.
        roller_y = self.height + self.roller_radius
        left_roller = qtc.QRectF(
            -self.width / 3.0 - self.roller_radius,
            roller_y - self.roller_radius,
            2.0 * self.roller_radius,
            2.0 * self.roller_radius,
        )
        right_roller = qtc.QRectF(
            self.width / 3.0 - self.roller_radius,
            roller_y - self.roller_radius,
            2.0 * self.roller_radius,
            2.0 * self.roller_radius,
        )
        painter.drawEllipse(left_roller)
        painter.drawEllipse(right_roller)

        ground_y = self.height + 3.0 * self.roller_radius
        painter.drawLine(-self.width, ground_y, self.width, ground_y)

        hatch_brush = qtg.QBrush(qtc.Qt.BDiagPattern)
        painter.setBrush(hatch_brush)
        painter.setPen(qtg.QPen(qtc.Qt.NoPen))
        painter.drawRect(qtc.QRectF(-self.width, ground_y, 2.0 * self.width, 2.0 * self.roller_radius))

        self.rect = qtc.QRectF(
            -self.width,
            -pivot_radius,
            2.0 * self.width,
            self.height + 6.0 * self.roller_radius,
        )
        self.transformation.reset()
        self.transformation.translate(self.x, self.y)
        self.transformation.rotate(self.rotation_angle)
        self.setTransform(self.transformation)
        self.transformation.reset()
#endregion


#region model helper definitions
class Position:
    # Chat GPT helped me write this function.
    def __init__(self, pos=None, x=None, y=None, z=None):
        """
        Store a point or vector in 3D space.

        Args:
            pos: Optional tuple in the form (x, y, z).
            x: Optional x-coordinate override.
            y: Optional y-coordinate override.
            z: Optional z-coordinate override.

        Returns:
            None.
        """
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

        if pos is not None:
            self.x, self.y, self.z = pos

        self.x = x if x is not None else self.x
        self.y = y if y is not None else self.y
        self.z = z if z is not None else self.z

    # Chat GPT helped me write this function.
    def __eq__(self, other):
        """
        Compare two positions by coordinate value.

        Args:
            other: Position being compared.

        Returns:
            True when x, y, and z all match; otherwise False.
        """
        return self.x == other.x and self.y == other.y and self.z == other.z

    # Chat GPT helped me write this function.
    def __add__(self, other):
        """
        Add two positions component by component.

        Args:
            other: Position to add.

        Returns:
            New Position containing the sum.
        """
        return Position((self.x + other.x, self.y + other.y, self.z + other.z))

    # Chat GPT helped me write this function.
    def __iadd__(self, other):
        """
        Add a scalar or position into this position.

        Args:
            other: Scalar or Position to add.

        Returns:
            The updated Position.
        """
        if isinstance(other, (float, int)):
            self.x += other
            self.y += other
            self.z += other
        elif isinstance(other, Position):
            self.x += other.x
            self.y += other.y
            self.z += other.z
        return self

    # Chat GPT helped me write this function.
    def __sub__(self, other):
        """
        Subtract another position component by component.

        Args:
            other: Position to subtract.

        Returns:
            New Position containing the difference.
        """
        return Position((self.x - other.x, self.y - other.y, self.z - other.z))

    # Chat GPT helped me write this function.
    def __isub__(self, other):
        """
        Subtract a scalar or position from this position.

        Args:
            other: Scalar or Position to subtract.

        Returns:
            The updated Position.
        """
        if isinstance(other, (float, int)):
            self.x -= other
            self.y -= other
            self.z -= other
        elif isinstance(other, Position):
            self.x -= other.x
            self.y -= other.y
            self.z -= other.z
        return self

    # Chat GPT helped me write this function.
    def __mul__(self, other):
        """
        Multiply this position by a scalar or another position.

        Args:
            other: Scalar multiplier or Position for component multiplication.

        Returns:
            New Position containing the product.
        """
        if isinstance(other, (float, int)):
            return Position((self.x * other, self.y * other, self.z * other))
        if isinstance(other, Position):
            return Position((self.x * other.x, self.y * other.y, self.z * other.z))
        return NotImplemented

    # Chat GPT helped me write this function.
    def __rmul__(self, other):
        """
        Multiply this position when the scalar is on the left side.

        Args:
            other: Scalar multiplier.

        Returns:
            New Position containing the product.
        """
        return self * other

    # Chat GPT helped me write this function.
    def __imul__(self, other):
        """
        Multiply this position in place by a scalar.

        Args:
            other: Scalar multiplier.

        Returns:
            The updated Position.
        """
        if isinstance(other, (float, int)):
            self.x *= other
            self.y *= other
            self.z *= other
        return self

    # Chat GPT helped me write this function.
    def __truediv__(self, other):
        """
        Divide this position by a scalar.

        Args:
            other: Scalar divisor.

        Returns:
            New Position containing the quotient.
        """
        if isinstance(other, (float, int)):
            return Position((self.x / other, self.y / other, self.z / other))
        return NotImplemented

    # Chat GPT helped me write this function.
    def __idiv__(self, other):
        """
        Divide this position in place by a scalar.

        Args:
            other: Scalar divisor.

        Returns:
            The updated Position.
        """
        if isinstance(other, (float, int)):
            self.x /= other
            self.y /= other
            self.z /= other
        return self

    # Chat GPT helped me write this function.
    def set_values(self, position_text=None, position_tuple=None):
        """
        Update the position from a comma-delimited string or tuple.

        Args:
            position_text: Optional string like "x, y, z".
            position_tuple: Optional tuple like (x, y, z).

        Returns:
            None.
        """
        if position_text is not None:
            cells = position_text.replace("(", "").replace(")", "").strip().split(",")
            self.x = float(cells[0])
            self.y = float(cells[1])
            self.z = float(cells[2])
        elif position_tuple is not None:
            self.x, self.y, self.z = [float(value) for value in position_tuple]

    # Chat GPT helped me write this function.
    def as_tuple(self):
        """
        Return the position coordinates as a tuple.

        Args:
            None.

        Returns:
            Tuple in the form (x, y, z).
        """
        return self.x, self.y, self.z

    # Chat GPT helped me write this function.
    def as_string(self, places=3):
        """
        Return the position coordinates as a formatted string.

        Args:
            places: Number of decimal places to show.

        Returns:
            String containing x, y, and z values.
        """
        return "{}, {}, {}".format(round(self.x, places), round(self.y, places), round(self.z, places))

    # Chat GPT helped me write this function.
    def magnitude(self):
        """
        Calculate the vector magnitude.

        Args:
            None.

        Returns:
            Euclidean magnitude of the position vector.
        """
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    # Chat GPT helped me write this function.
    def normalize(self):
        """
        Convert this position vector to a unit vector when possible.

        Args:
            None.

        Returns:
            None.
        """
        length = self.magnitude()
        if length <= 0.0:
            return
        self.__idiv__(length)

    # Chat GPT helped me write this function.
    def angle_radians(self):
        """
        Calculate the x-y plane angle of this vector in radians.

        Args:
            None.

        Returns:
            Angle in radians measured counterclockwise from positive x.
        """
        length = self.magnitude()
        if length <= 0.0:
            return 0.0
        if self.y >= 0.0:
            return math.acos(self.x / length)
        return 2.0 * math.pi - math.acos(self.x / length)

    # Chat GPT helped me write this function.
    def angle_degrees(self):
        """
        Calculate the x-y plane angle of this vector in degrees.

        Args:
            None.

        Returns:
            Angle in degrees measured counterclockwise from positive x.
        """
        return 180.0 / math.pi * self.angle_radians()


class Rectangle:
    # Chat GPT helped me write this function.
    def __init__(self, top=None, left=None, bottom=None, right=None):
        """
        Store rectangular bounds around the truss.

        Args:
            top: Upper y-coordinate.
            left: Left x-coordinate.
            bottom: Lower y-coordinate.
            right: Right x-coordinate.

        Returns:
            None.
        """
        self.top = 0.0 if top is None else top
        self.left = 0.0 if left is None else left
        self.bottom = 0.0 if bottom is None else bottom
        self.right = 0.0 if right is None else right

    # Chat GPT helped me write this function.
    def height(self):
        """
        Calculate the rectangle height.

        Args:
            None.

        Returns:
            Rectangle height.
        """
        return self.top - self.bottom

    # Chat GPT helped me write this function.
    def width(self):
        """
        Calculate the rectangle width.

        Args:
            None.

        Returns:
            Rectangle width.
        """
        return self.right - self.left

    # Chat GPT helped me write this function.
    def center_y(self):
        """
        Calculate the y-coordinate of the rectangle center.

        Args:
            None.

        Returns:
            Center y-coordinate.
        """
        return self.bottom + self.height() / 2.0

    # Chat GPT helped me write this function.
    def center_x(self):
        """
        Calculate the x-coordinate of the rectangle center.

        Args:
            None.

        Returns:
            Center x-coordinate.
        """
        return self.left + self.width() / 2.0


class Material:
    # Chat GPT helped me write this function.
    def __init__(self, uts=None, ys=None, modulus=None, static_factor=None):
        """
        Store the global material strength values from the input file.

        Args:
            uts: Ultimate tensile strength.
            ys: Yield strength.
            modulus: Modulus of elasticity.
            static_factor: Static factor of safety.

        Returns:
            None.
        """
        self.uts = 0.0 if uts is None else uts
        self.ys = 0.0 if ys is None else ys
        self.modulus = 0.0 if modulus is None else modulus
        self.static_factor = 0.0 if static_factor is None else static_factor


class Node:
    # Chat GPT helped me write this function.
    def __init__(self, name=None, position=None):
        """
        Store one truss node and its calculated support/load information.

        Args:
            name: Node name from the input file.
            position: Position object for the node coordinates.

        Returns:
            None.
        """
        self.name = name
        self.position = position if position is not None else Position()
        self.graphic = None
        self.support_type = "free"
        self.self_weight_load_lb = 0.0
        self.reaction_load_lb = 0.0

    # Chat GPT helped me write this function.
    def __eq__(self, other):
        """
        Compare two nodes by name and position.

        Args:
            other: Node being compared.

        Returns:
            True when both nodes have the same name and position.
        """
        return self.name == other.name and self.position == other.position

    # Chat GPT helped me write this function.
    def tooltip_text(self, support_summary=""):
        """
        Build the hover tooltip text for this node.

        Args:
            support_summary: Optional text showing the left and right support reactions.

        Returns:
            Multi-line tooltip string for the node.
        """
        lines = [
            "Node: {}".format(self.name),
            "support: {}".format(self.support_type),
            "x: {:0.3f}, y: {:0.3f}".format(self.position.x, self.position.y),
            "self-weight load: {:0.2f} lb downward".format(self.self_weight_load_lb),
        ]
        if self.reaction_load_lb > 0.0:
            lines.append("vertical reaction: {:0.2f} lb upward".format(self.reaction_load_lb))
        if support_summary:
            lines.append(support_summary)
        return "\n".join(lines)


class Link:
    # Chat GPT helped me write this function.
    def __init__(
        self,
        name="",
        node1_name="1",
        node2_name="2",
        material=DEFAULT_LINK_MATERIAL,
        width_in=DEFAULT_LINK_WIDTH_IN,
        thickness_in=DEFAULT_LINK_THICKNESS_IN,
    ):
        """
        Store one truss link and the section data needed for weight.

        Args:
            name: Link name from the input file.
            node1_name: First endpoint node name.
            node2_name: Second endpoint node name.
            material: Link material name used for density.
            width_in: Link width in inches.
            thickness_in: Link thickness in inches.

        Returns:
            None.
        """
        self.name = name
        self.node1_name = node1_name
        self.node2_name = node2_name
        self.material = material
        self.width_in = width_in
        self.thickness_in = thickness_in
        self.length_in = 0.0
        self.angle_rad = 0.0
        self.weight_lb = 0.0
        self.graphic = None

    # Chat GPT helped me write this function.
    def __eq__(self, other):
        """
        Compare two links by endpoints, geometry, and section properties.

        Args:
            other: Link being compared.

        Returns:
            True when the links have matching stored values.
        """
        return (
            self.node1_name == other.node1_name
            and self.node2_name == other.node2_name
            and self.length_in == other.length_in
            and self.angle_rad == other.angle_rad
            and self.material == other.material
            and self.width_in == other.width_in
            and self.thickness_in == other.thickness_in
        )

    # Chat GPT helped me write this function.
    def set_geometry(self, node1, node2):
        """
        Calculate and store link length and angle from its endpoint nodes.

        Args:
            node1: First endpoint Node.
            node2: Second endpoint Node.

        Returns:
            None.
        """
        link_vector = node2.position - node1.position
        self.length_in = link_vector.magnitude()
        self.angle_rad = link_vector.angle_radians()

    # Chat GPT helped me write this function.
    def cross_section_area_in2(self):
        """
        Calculate the rectangular link cross-sectional area.

        Args:
            None.

        Returns:
            Cross-sectional area in square inches.
        """
        return self.width_in * self.thickness_in

    # Chat GPT helped me write this function.
    def density_lb_per_in3(self):
        """
        Look up the density for this link material.

        Args:
            None.

        Returns:
            Material density in pounds per cubic inch.
        """
        return DENSITY_LB_PER_IN3.get(self.material, DENSITY_LB_PER_IN3[DEFAULT_LINK_MATERIAL])

    # Chat GPT helped me write this function.
    def calculate_weight(self):
        """
        Calculate and store the link weight from density, length, width, and thickness.

        Args:
            None.

        Returns:
            Link weight in pounds.
        """
        volume_in3 = self.length_in * self.cross_section_area_in2()
        self.weight_lb = volume_in3 * self.density_lb_per_in3()
        return self.weight_lb

    # Chat GPT helped me write this function.
    def tooltip_text(self):
        """
        Build the hover tooltip text for this link.

        Args:
            None.

        Returns:
            Multi-line tooltip string for the link.
        """
        return "\n".join(
            [
                "link name = {}".format(self.name),
                "nodes: {} to {}".format(self.node1_name, self.node2_name),
                "length: {:0.3f} in".format(self.length_in),
                "angle: {:0.3f} deg".format(self.angle_rad * 180.0 / math.pi),
                "material: {}".format(self.material.title()),
                "width: {:0.3f} in".format(self.width_in),
                "thickness: {:0.3f} in".format(self.thickness_in),
                "weight: {:0.2f} lb".format(self.weight_lb),
            ]
        )


class TrussModel:
    # Chat GPT helped me write this function.
    def __init__(self):
        """
        Store all model data for the current truss design.

        Args:
            None.

        Returns:
            None.
        """
        self.title = None
        self.links = []
        self.nodes = []
        self.material = Material()
        self.rct = Rectangle()
        self.left_support_name = None
        self.right_support_name = None

    # Chat GPT helped me write this function.
    def get_node(self, name):
        """
        Find a node by name.

        Args:
            name: Node name to look up.

        Returns:
            Matching Node when found, otherwise None.
        """
        for node in self.nodes:
            if node.name == name:
                return node
        return None

    # Chat GPT helped me write this function.
    def get_center_point(self):
        """
        Calculate the rectangle enclosing all truss nodes.

        Args:
            None.

        Returns:
            Rectangle containing all nodes.
        """
        if not self.nodes:
            self.rct = Rectangle()
            return self.rct

        rct = Rectangle(
            left=self.nodes[0].position.x,
            right=self.nodes[0].position.x,
            top=self.nodes[0].position.y,
            bottom=self.nodes[0].position.y,
        )

        for node in self.nodes:
            rct.left = min(rct.left, node.position.x)
            rct.right = max(rct.right, node.position.x)
            rct.top = max(rct.top, node.position.y)
            rct.bottom = min(rct.bottom, node.position.y)

        self.rct = rct
        return self.rct

    # Chat GPT helped me write this function.
    def support_nodes(self):
        """
        Return the left and right support nodes.

        Args:
            None.

        Returns:
            Tuple containing left support Node and right support Node.
        """
        return self.get_node(self.left_support_name), self.get_node(self.right_support_name)

    # Chat GPT helped me write this function.
    def total_weight_lb(self):
        """
        Sum the weight of every link in the truss.

        Args:
            None.

        Returns:
            Total truss link weight in pounds.
        """
        return sum(link.weight_lb for link in self.links)
#endregion


#region view definitions
class TrussView:
    # Chat GPT helped me write this function.
    def __init__(self):
        """
        Create the Qt scene and default widgets used by the truss view.

        Args:
            None.

        Returns:
            None.
        """
        self.scene = qtw.QGraphicsScene()
        self.te_report = qtw.QTextEdit()
        self.le_long_link_name = qtw.QLineEdit()
        self.le_long_link_node1 = qtw.QLineEdit()
        self.le_long_link_node2 = qtw.QLineEdit()
        self.le_long_link_length = qtw.QLineEdit()
        self.gv = qtw.QGraphicsView()

        # Pens and brushes are centralized so drawing style is easy to adjust.
        self.pen_link = qtg.QPen(qtg.QColor("orange"))
        self.pen_link.setWidth(1)

        self.pen_node = qtg.QPen(qtc.Qt.darkBlue)
        self.pen_node.setStyle(qtc.Qt.SolidLine)
        self.pen_node.setWidth(1)

        self.pen_label = qtg.QPen(qtc.Qt.darkMagenta)
        self.pen_label.setStyle(qtc.Qt.SolidLine)
        self.pen_label.setWidth(1)

        self.pen_grid_lines = qtg.QPen()
        self.pen_grid_lines.setWidth(1)
        self.pen_grid_lines.setColor(qtg.QColor.fromHsv(197, 144, 228, alpha=50))

        self.brush_link = qtg.QBrush(qtg.QColor.fromHsv(35, 255, 255, 64))
        self.brush_pivot = qtg.QBrush(qtg.QColor.fromRgb(215, 215, 215, alpha=128))
        self.brush_node = qtg.QBrush(qtg.QColor.fromCmyk(0, 0, 255, 0, alpha=100))
        self.brush_grid = qtg.QBrush(qtg.QColor.fromHsv(87, 98, 245, alpha=128))

    # Chat GPT helped me write this function.
    def set_display_widgets(self, widgets):
        """
        Attach GUI widgets to the view.

        Args:
            widgets: Tuple containing report fields and the graphics view.

        Returns:
            None.
        """
        self.te_report = widgets[0]
        self.le_long_link_name = widgets[1]
        self.le_long_link_node1 = widgets[2]
        self.le_long_link_node2 = widgets[3]
        self.le_long_link_length = widgets[4]
        self.gv = widgets[5]
        self.gv.setScene(self.scene)

    # Chat GPT helped me write this function.
    def install_scene_event_filter(self, event_filter):
        """
        Install the app window as the scene event filter.

        Args:
            event_filter: QObject that will receive scene events.

        Returns:
            None.
        """
        self.scene.installEventFilter(event_filter)

    # Chat GPT helped me write this function.
    def is_scene(self, obj):
        """
        Check whether a Qt object is the truss graphics scene.

        Args:
            obj: Qt object being checked.

        Returns:
            True when obj is this view's scene.
        """
        return obj == self.scene

    # Chat GPT helped me write this function.
    def mouse_position_text(self, scene_position, transform):
        """
        Build the mouse tracker text for the status label.

        Args:
            scene_position: Mouse position in scene coordinates.
            transform: Current graphics view transform.

        Returns:
            Formatted mouse tracker string.
        """
        text = "Mouse Position:  x = {}, y = {}".format(
            round(scene_position.x(), 2),
            round(-scene_position.y(), 2),
        )

        item = self.item_at(scene_position, transform)
        if item is not None and item.data(0) is not None:
            text += " ({})".format(item.data(0))

        item_names = [item.name if hasattr(item, "name") else None for item in self.items_at(scene_position)]
        for item_name in item_names:
            text += ", " + (item_name if item_name is not None else "none")

        return text

    # Chat GPT helped me write this function.
    def item_at(self, scene_position, transform):
        """
        Return the top graphics item at a scene position.

        Args:
            scene_position: Mouse position in scene coordinates.
            transform: Current graphics view transform.

        Returns:
            QGraphicsItem under the mouse, or None.
        """
        return self.scene.itemAt(scene_position, transform)

    # Chat GPT helped me write this function.
    def items_at(self, scene_position):
        """
        Return all graphics items at a scene position.

        Args:
            scene_position: Mouse position in scene coordinates.

        Returns:
            List of QGraphicsItem objects under the mouse.
        """
        return self.scene.items(scene_position)

    # Chat GPT helped me write this function.
    def display_report(self, truss=None):
        """
        Display the design report and longest-link values in the GUI.

        Args:
            truss: TrussModel to display.

        Returns:
            None.
        """
        if truss is None:
            return

        longest_link = None
        for link in truss.links:
            if longest_link is None or link.length_in > longest_link.length_in:
                longest_link = link

        self.te_report.setText(self.make_report_text(truss))

        if longest_link is None:
            return

        self.le_long_link_name.setText(longest_link.name)
        self.le_long_link_length.setText("{:0.2f}".format(longest_link.length_in))
        self.le_long_link_node1.setText(longest_link.node1_name)
        self.le_long_link_node2.setText(longest_link.node2_name)

    # Chat GPT helped me write this function.
    def make_report_text(self, truss):
        """
        Build the formatted truss design report.

        Args:
            truss: TrussModel containing nodes, links, materials, and support loads.

        Returns:
            Multi-line report string for the GUI and console.
        """
        left_support, right_support = truss.support_nodes()
        left_reaction = 0.0 if left_support is None else left_support.reaction_load_lb
        right_reaction = 0.0 if right_support is None else right_support.reaction_load_lb

        report = "\tTruss Design Report\n"
        report += "Title:  {}\n".format(truss.title)
        report += "Static Factor of Safety:  {:0.2f}\n".format(truss.material.static_factor)
        report += "Ultimate Strength:  {:0.2f} ksi\n".format(truss.material.uts)
        report += "Yield Strength:  {:0.2f} ksi\n".format(truss.material.ys)
        report += "Modulus of Elasticity:  {:0.2f} Mpsi\n".format(truss.material.modulus)
        report += "Total Truss Weight:  {:0.2f} lb\n".format(truss.total_weight_lb())
        report += "Left Vertical Reaction from Weight:  {:0.2f} lb\n".format(left_reaction)
        report += "Right Vertical Reaction from Weight: {:0.2f} lb\n".format(right_reaction)
        report += "_________________________Link Summary_________________________\n"
        report += "Link\t(1)\t(2)\tLength(in)\tAngle(deg)\tMaterial\tWidth(in)\tThick(in)\tWeight(lb)\n"

        for link in truss.links:
            report += "{}\t{}\t{}\t{:0.2f}\t\t{:0.2f}\t\t{}\t{:0.2f}\t\t{:0.2f}\t\t{:0.2f}\n".format(
                link.name,
                link.node1_name,
                link.node2_name,
                link.length_in,
                link.angle_rad * 180.0 / math.pi,
                link.material.title(),
                link.width_in,
                link.thickness_in,
                link.weight_lb,
            )

        return report

    # Chat GPT helped me write this function.
    def build_scene(self, truss=None):
        """
        Rebuild the grid, links, nodes, and supports for the current truss.

        Args:
            truss: TrussModel to draw.

        Returns:
            None.
        """
        if truss is None or not truss.nodes:
            return

        rct = truss.get_center_point()
        rct.left -= 50.0
        rct.right += 50.0
        rct.top += 50.0
        rct.bottom -= 50.0

        self.scene.clear()
        self.draw_grid(
            delta_x=10,
            delta_y=10,
            height=abs(rct.height()),
            width=abs(rct.width()),
            center_x=0,
            center_y=0,
        )
        self.draw_links(truss=truss)
        self.draw_nodes(truss=truss)

    # Chat GPT helped me write this function.
    def draw_grid(self, delta_x=10, delta_y=10, height=320, width=180, center_x=120, center_y=60):
        """
        Draw a background grid for visual reference.

        Args:
            delta_x: Grid spacing in the x direction.
            delta_y: Grid spacing in the y direction.
            height: Grid height.
            width: Grid width.
            center_x: Scene x-coordinate for grid center.
            center_y: Scene y-coordinate for grid center.

        Returns:
            None.
        """
        left = center_x - width / 2.0
        right = center_x + width / 2.0
        top = center_y - height / 2.0
        bottom = center_y + height / 2.0

        background = qtw.QGraphicsRectItem(left, top, width, height)
        background.setBrush(self.brush_grid)
        background.setPen(self.pen_grid_lines)
        self.scene.addItem(background)

        # Draw vertical grid lines.
        x_value = left
        while x_value <= right:
            line = qtw.QGraphicsLineItem(x_value, top, x_value, bottom)
            line.setPen(self.pen_grid_lines)
            self.scene.addItem(line)
            x_value += delta_x

        # Draw horizontal grid lines.
        y_value = bottom
        while y_value >= top:
            line = qtw.QGraphicsLineItem(left, y_value, right, y_value)
            line.setPen(self.pen_grid_lines)
            self.scene.addItem(line)
            y_value -= delta_y

    # Chat GPT helped me write this function.
    def draw_links(self, truss=None):
        """
        Draw each truss link in the scene.

        Args:
            truss: TrussModel containing links and nodes.

        Returns:
            None.
        """
        if truss is None:
            return

        rct = truss.get_center_point()
        offset = Position(x=rct.center_x(), y=rct.center_y())

        for link in truss.links:
            node1 = truss.get_node(link.node1_name)
            node2 = truss.get_node(link.node2_name)
            if node1 is None or node2 is None:
                continue

            start_x = node1.position.x - offset.x
            start_y = -(node1.position.y - offset.y)
            end_x = node2.position.x - offset.x
            end_y = -(node2.position.y - offset.y)
            item_name = "link name = {}".format(link.name)

            link.graphic = TrussLinkItem(
                start_x,
                start_y,
                end_x,
                end_y,
                radius=3,
                pen=self.pen_link,
                brush=self.brush_link,
                name=item_name,
                tooltip_text=link.tooltip_text(),
            )
            self.scene.addItem(link.graphic)

    # Chat GPT helped me write this function.
    def draw_nodes(self, truss=None):
        """
        Draw all truss nodes and support symbols.

        Args:
            truss: TrussModel containing nodes and calculated support types.

        Returns:
            None.
        """
        if truss is None:
            return

        rct = truss.get_center_point()
        offset = Position(x=rct.center_x(), y=rct.center_y())
        left_support, right_support = truss.support_nodes()
        support_summary = ""

        if left_support is not None and right_support is not None:
            support_summary = "left reaction: {:0.2f} lb\nright reaction: {:0.2f} lb".format(
                left_support.reaction_load_lb,
                right_support.reaction_load_lb,
            )

        for node in truss.nodes:
            x_value = node.position.x - offset.x
            y_value = node.position.y - offset.y
            tooltip = node.tooltip_text(support_summary=support_summary)

            if node.support_type == "pin":
                node.graphic = RigidPivotPoint(
                    x_value,
                    -y_value,
                    10,
                    18,
                    brush=self.brush_pivot,
                    pen=self.pen_node,
                    name=node.name,
                )
                node.graphic.setToolTip(tooltip)
                node.graphic.setData(0, node.name)
                self.scene.addItem(node.graphic)
            elif node.support_type == "roller":
                node.graphic = RollerSupport(
                    x_value,
                    -y_value,
                    10,
                    18,
                    brush=self.brush_pivot,
                    pen=self.pen_node,
                    name=node.name,
                    tooltip_text=tooltip,
                )
                self.scene.addItem(node.graphic)
            else:
                self.draw_circle(
                    center_x=x_value,
                    center_y=y_value,
                    radius=6,
                    pen=self.pen_node,
                    brush=self.brush_node,
                    name=node.name,
                    tooltip=tooltip,
                )

            self.draw_label(x=x_value - 5.0, y=y_value + 15.0, text=node.name, pen=self.pen_label)

    # Chat GPT helped me write this function.
    def draw_label(self, x, y, text="", pen=None, brush=None, tooltip=None):
        """
        Draw a text label at the requested truss coordinate.

        Args:
            x: Model x-coordinate for the label.
            y: Model y-coordinate for the label.
            text: Label text to display.
            pen: Optional pen controlling label color.
            brush: Optional brush for a label background.
            tooltip: Optional tooltip for the label.

        Returns:
            None.
        """
        label = qtw.QGraphicsTextItem(text)
        width = label.boundingRect().width()
        height = label.boundingRect().height()
        label.setX(x - width / 2.0)
        label.setY(-y - height / 2.0)

        if tooltip is not None:
            label.setToolTip(tooltip)
        if pen is not None:
            label.setDefaultTextColor(pen.color())
        if brush is not None:
            background = qtw.QGraphicsRectItem(label.x(), label.y(), width, height)
            background.setBrush(brush)
            background.setPen(qtg.QPen(brush.color()))
            self.scene.addItem(background)

        self.scene.addItem(label)

    # Chat GPT helped me write this function.
    def draw_circle(self, center_x, center_y, radius, angle=0, brush=None, pen=None, name=None, tooltip=None):
        """
        Draw a circular node marker.

        Args:
            center_x: Model x-coordinate for the circle center.
            center_y: Model y-coordinate for the circle center.
            radius: Circle radius.
            angle: Unused angle kept for compatibility with the drawing pattern.
            brush: Optional fill brush.
            pen: Optional outline pen.
            name: Optional item name used by the mouse tracker.
            tooltip: Optional hover tooltip.

        Returns:
            None.
        """
        ellipse = qtw.QGraphicsEllipseItem(
            center_x - radius,
            -1.0 * (center_y + radius),
            2.0 * radius,
            2.0 * radius,
        )

        if pen is not None:
            ellipse.setPen(pen)
        if brush is not None:
            ellipse.setBrush(brush)
        if name is not None:
            ellipse.setData(0, name)
            ellipse.name = name
        if tooltip is not None:
            ellipse.setToolTip(tooltip)

        self.scene.addItem(ellipse)
#endregion


#region controller definitions
class TrussController:
    # Chat GPT helped me write this function.
    def __init__(self):
        """
        Create the truss controller, model, and view.

        Args:
            None.

        Returns:
            None.
        """
        self.truss = TrussModel()
        self.view = TrussView()

    # Chat GPT helped me write this function.
    def import_from_file(self, data):
        """
        Read a truss input file and refresh the report and drawing.

        Args:
            data: List of text lines from the input file.

        Returns:
            None.
        """
        self.truss = TrussModel()

        for line in data:
            self.parse_input_line(line)

        self.choose_support_nodes()
        self.calculate_link_values()
        self.calculate_support_reactions()
        self.display_report()
        self.draw_truss()

        # Print labeled results for graders running from a console.
        print(self.view.make_report_text(self.truss))

    # Chat GPT helped me write this function.
    def parse_input_line(self, line):
        """
        Parse one non-comment line from the truss input file.

        Args:
            line: Raw input line from the file.

        Returns:
            None.
        """
        clean_line = self.clean_input_line(line)
        if not clean_line:
            return

        cells = [cell.strip() for cell in clean_line.split(",")]
        keyword = cells[0].lower()

        if keyword == "title":
            self.truss.title = self.clean_text(",".join(cells[1:]))
        elif keyword == "material":
            self.parse_global_material(cells)
        elif keyword.startswith("static"):
            self.parse_static_factor(cells)
        elif keyword == "node":
            self.parse_node(cells)
        elif keyword == "link":
            self.parse_link(cells)

    # Chat GPT helped me write this function.
    def clean_input_line(self, line):
        """
        Remove comments and outside whitespace from an input line.

        Args:
            line: Raw input line from the file.

        Returns:
            Clean line text, or an empty string when the line has no data.
        """
        return line.split("#", 1)[0].strip()

    # Chat GPT helped me write this function.
    def clean_text(self, text):
        """
        Remove surrounding whitespace and quotes from text input.

        Args:
            text: Text value from an input cell.

        Returns:
            Cleaned text value.
        """
        return text.strip().strip("'").strip('"')

    # Chat GPT helped me write this function.
    def parse_global_material(self, cells):
        """
        Parse the global strength material line.

        Args:
            cells: Comma-split cells from a material input line.

        Returns:
            None.
        """
        if len(cells) < 4:
            return

        sut = self.parse_float(cells[1], default=0.0)
        sy = self.parse_float(cells[2], default=0.0)
        modulus = self.parse_float(cells[3], default=0.0)
        self.truss.material.uts = sut
        self.truss.material.ys = sy
        self.truss.material.modulus = modulus

    # Chat GPT helped me write this function.
    def parse_static_factor(self, cells):
        """
        Parse the static factor of safety line.

        Args:
            cells: Comma-split cells from a static factor input line.

        Returns:
            None.
        """
        if len(cells) < 2:
            return
        self.truss.material.static_factor = self.parse_float(cells[1], default=0.0)

    # Chat GPT helped me write this function.
    def parse_node(self, cells):
        """
        Parse a node line and add it to the model.

        Args:
            cells: Comma-split cells from a node input line.

        Returns:
            None.
        """
        if len(cells) < 4:
            return

        name = self.clean_text(cells[1])
        x_value = self.parse_float(cells[2], default=0.0)
        y_value = self.parse_float(cells[3], default=0.0)
        node = Node(name=name, position=Position(x=x_value, y=y_value))

        if not self.has_node(name):
            self.add_node(node)

    # Chat GPT helped me write this function.
    def parse_link(self, cells):
        """
        Parse a link line and add it to the model.

        Args:
            cells: Comma-split cells from a link input line.

        Returns:
            None.
        """
        if len(cells) < 4:
            return

        name = self.clean_text(cells[1])
        node1_name = self.clean_text(cells[2])
        node2_name = self.clean_text(cells[3])
        material = self.normalize_material(cells[4]) if len(cells) > 4 else DEFAULT_LINK_MATERIAL
        width_in = self.parse_float(cells[5], default=DEFAULT_LINK_WIDTH_IN) if len(cells) > 5 else DEFAULT_LINK_WIDTH_IN
        thickness_in = (
            self.parse_float(cells[6], default=DEFAULT_LINK_THICKNESS_IN)
            if len(cells) > 6
            else DEFAULT_LINK_THICKNESS_IN
        )

        link = Link(
            name=name,
            node1_name=node1_name,
            node2_name=node2_name,
            material=material,
            width_in=width_in,
            thickness_in=thickness_in,
        )
        self.add_link(link)

    # Chat GPT helped me write this function.
    def parse_float(self, text, default=0.0):
        """
        Safely parse a floating-point value.

        Args:
            text: Text to parse as a number.
            default: Value returned when parsing fails.

        Returns:
            Parsed float or the provided default.
        """
        try:
            return float(self.clean_text(text))
        except (TypeError, ValueError):
            return default

    # Chat GPT helped me write this function.
    def normalize_material(self, material_text):
        """
        Normalize a link material name for density lookup.

        Args:
            material_text: Material text from the link row.

        Returns:
            Normalized material key.
        """
        material = self.clean_text(material_text).lower()
        if material in ("al", "alum", "aluminum", "aluminium"):
            return "aluminum"
        if material in ("steel", "stl"):
            return "steel"
        return DEFAULT_LINK_MATERIAL

    # Chat GPT helped me write this function.
    def has_node(self, name):
        """
        Check whether a node name already exists in the model.

        Args:
            name: Node name to check.

        Returns:
            True when the model already contains the node.
        """
        return self.truss.get_node(name) is not None

    # Chat GPT helped me write this function.
    def add_node(self, node):
        """
        Add a node to the model.

        Args:
            node: Node object to append.

        Returns:
            None.
        """
        self.truss.nodes.append(node)

    # Chat GPT helped me write this function.
    def get_node(self, name):
        """
        Return a node from the model by name.

        Args:
            name: Node name to look up.

        Returns:
            Matching Node when found, otherwise None.
        """
        return self.truss.get_node(name)

    # Chat GPT helped me write this function.
    def add_link(self, link):
        """
        Add a link to the model.

        Args:
            link: Link object to append.

        Returns:
            None.
        """
        self.truss.links.append(link)

    # Chat GPT helped me write this function.
    def calculate_link_values(self):
        """
        Calculate geometry and weight for every link.

        Args:
            None.

        Returns:
            None.
        """
        for link in self.truss.links:
            node1 = self.get_node(link.node1_name)
            node2 = self.get_node(link.node2_name)
            if node1 is None or node2 is None:
                continue

            link.set_geometry(node1, node2)
            link.calculate_weight()

    # Chat GPT helped me write this function.
    def choose_support_nodes(self):
        """
        Select the left pin and right roller supports from node x-positions.

        Args:
            None.

        Returns:
            None.
        """
        if not self.truss.nodes:
            return

        sorted_nodes = sorted(self.truss.nodes, key=lambda node: (node.position.x, node.position.y, node.name))
        left_support = sorted_nodes[0]
        right_support = sorted_nodes[-1]

        for node in self.truss.nodes:
            node.support_type = "free"

        left_support.support_type = "pin"
        right_support.support_type = "roller"
        self.truss.left_support_name = left_support.name
        self.truss.right_support_name = right_support.name

    # Chat GPT helped me write this function.
    def calculate_support_reactions(self):
        """
        Calculate nodal self-weight loads and left/right vertical reactions.

        Args:
            None.

        Returns:
            None.
        """
        for node in self.truss.nodes:
            node.self_weight_load_lb = 0.0
            node.reaction_load_lb = 0.0

        # Split each member weight equally to its endpoint nodes.
        for link in self.truss.links:
            node1 = self.get_node(link.node1_name)
            node2 = self.get_node(link.node2_name)
            if node1 is None or node2 is None:
                continue
            end_load = link.weight_lb / 2.0
            node1.self_weight_load_lb += end_load
            node2.self_weight_load_lb += end_load

        left_support, right_support = self.truss.support_nodes()
        if left_support is None and right_support is None:
            return
        if right_support is None or right_support == left_support:
            left_support.reaction_load_lb = self.truss.total_weight_lb()
            return

        support_span = right_support.position.x - left_support.position.x
        if abs(support_span) <= 1.0e-9:
            left_support.reaction_load_lb = self.truss.total_weight_lb()
            return

        moment_about_left = 0.0
        for node in self.truss.nodes:
            arm = node.position.x - left_support.position.x
            moment_about_left += node.self_weight_load_lb * arm

        right_reaction = moment_about_left / support_span
        left_reaction = self.truss.total_weight_lb() - right_reaction

        left_support.reaction_load_lb = left_reaction
        right_support.reaction_load_lb = right_reaction

    # Chat GPT helped me write this function.
    def set_display_widgets(self, widgets):
        """
        Pass GUI display widgets to the view.

        Args:
            widgets: Tuple containing report fields and graphics view.

        Returns:
            None.
        """
        self.view.set_display_widgets(widgets)

    # Chat GPT helped me write this function.
    def install_scene_event_filter(self, event_filter):
        """
        Install a scene event filter through the controller.

        Args:
            event_filter: QObject that should receive scene events.

        Returns:
            None.
        """
        self.view.install_scene_event_filter(event_filter)

    # Chat GPT helped me write this function.
    def is_scene(self, obj):
        """
        Tell the app whether an event object is the graphics scene.

        Args:
            obj: Qt object from the event filter.

        Returns:
            True when obj is the truss graphics scene.
        """
        return self.view.is_scene(obj)

    # Chat GPT helped me write this function.
    def mouse_position_text(self, scene_position, transform):
        """
        Get the mouse tracker text through the controller.

        Args:
            scene_position: Mouse position in scene coordinates.
            transform: Current graphics view transform.

        Returns:
            Formatted mouse tracker string.
        """
        return self.view.mouse_position_text(scene_position, transform)

    # Chat GPT helped me write this function.
    def display_report(self):
        """
        Ask the view to display the current truss report.

        Args:
            None.

        Returns:
            None.
        """
        self.view.display_report(truss=self.truss)

    # Chat GPT helped me write this function.
    def draw_truss(self):
        """
        Ask the view to rebuild the truss drawing.

        Args:
            None.

        Returns:
            None.
        """
        self.view.build_scene(truss=self.truss)
#endregion
