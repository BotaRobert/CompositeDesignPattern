import time

import cv2
import numpy as np
from abc import ABC, abstractmethod

# ==========================================
# Globals for Visualization
# ==========================================
WIDTH, HEIGHT = 800, 500
CANVAS = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
TREE_ROOT = None  # Will hold the top-level manager to orchestrate drawing


def update_display(delay_ms):
    """Clears the canvas, redraws the entire tree, and pauses."""
    CANVAS[:] = (240, 240, 240)  # Light gray background

    if TREE_ROOT:
        # 1. Draw connecting lines first (so they stay behind the shapes)
        TREE_ROOT.draw_connections(CANVAS)
        # 2. Draw the shapes and text on top
        TREE_ROOT.draw(CANVAS)

    cv2.imshow("Factory Hierarchy", CANVAS)
    cv2.waitKey(delay_ms)


# ==========================================
# Employee Classes
# ==========================================
class Employee(ABC):
    """The Component base class with layout and drawing data."""

    def __init__(self, emp_id: str):
        self.emp_id = emp_id
        # Tree coordinates
        self.x = 0
        self.y = 0
        # State machine for colors
        self.state = "IDLE"

    def get_color(self):
        """Returns BGR color based on work state."""
        if self.state == "WORKING":
            return (0, 200, 255)  # Yellow (BGR format)
        elif self.state == "DONE":
            return (100, 200, 100)  # Green
        return (200, 200, 200)  # Gray

    @abstractmethod
    def work(self):
        pass

    @abstractmethod
    def draw(self, canvas):
        pass

    def draw_connections(self, canvas):
        """Base case: Leaf nodes don't draw connections down."""
        pass


class FactoryWorker(Employee):
    """The Leaf class."""
    total_products_built = 0

    def work(self):
        # 1. Start Working
        self.state = "WORKING"
        update_display(1000)  # Replaces time.sleep(1.0)

        # 2. Do the work
        FactoryWorker.total_products_built += 1
        print(f"  [🛠️] Worker {self.emp_id} has built a product. (Total: {FactoryWorker.total_products_built})")

        # 3. Finish Working
        self.state = "DONE"
        update_display(50)

    def draw(self, canvas):
        color = self.get_color()
        # Draw a Circle for workers
        cv2.circle(canvas, (self.x, self.y), 30, color, -1)
        cv2.circle(canvas, (self.x, self.y), 30, (50, 50, 50), 2)  # Outline
        # ID Text
        cv2.putText(canvas, self.emp_id, (self.x - 22, self.y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)


class Supervisor(Employee):
    """The Composite class."""

    def __init__(self, emp_id: str):
        super().__init__(emp_id)
        self.subordinates = []

    def add_subordinate(self, employee: Employee):
        self.subordinates.append(employee)

    def work(self):
        # 1. Start Organizing Work
        self.state = "WORKING"
        update_display(500)  # Replaces time.sleep(0.5)

        subordinate_ids = [sub.emp_id for sub in self.subordinates]
        print(f"[📋] Supervisor {self.emp_id} has given work to: {subordinate_ids}")

        # 2. Delegate to subordinates
        for subordinate in self.subordinates:
            subordinate.work()

        # 3. Finish Work
        self.state = "DONE"
        update_display(50)

    def draw_connections(self, canvas):
        # Recursively draw lines from this supervisor to its subordinates
        for sub in self.subordinates:
            cv2.line(canvas, (self.x, self.y), (sub.x, sub.y), (150, 150, 150), 2)
            sub.draw_connections(canvas)

    def draw(self, canvas):
        color = self.get_color()
        # Draw a Rectangle for supervisors
        cv2.rectangle(canvas, (self.x - 30, self.y - 30), (self.x + 30, self.y + 30), color, -1)
        cv2.rectangle(canvas, (self.x - 30, self.y - 30), (self.x + 30, self.y + 30), (50, 50, 50), 2)  # Outline
        # ID Text
        cv2.putText(canvas, self.emp_id, (self.x - 22, self.y + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

        # Ensure subordinates are drawn on top of the lines
        for sub in self.subordinates:
            sub.draw(canvas)


# ==========================================
# Helper: Calculate Tree Layout
# ==========================================
def calculate_layout(node: Employee, depth=1, left=0, right=WIDTH):
    """Recursively assigns (x, y) coordinates to nodes so they form a neat tree."""
    node.y = depth * 120

    if isinstance(node, FactoryWorker):
        node.x = (left + right) // 2
    elif isinstance(node, Supervisor):
        num_children = len(node.subordinates)
        if num_children == 0:
            node.x = (left + right) // 2
        else:
            # Divide the horizontal space equally among children
            step = (right - left) // num_children
            for i, child in enumerate(node.subordinates):
                calculate_layout(child, depth + 1, left + i * step, left + (i + 1) * step)
            # Center the supervisor above its children
            node.x = sum(c.x for c in node.subordinates) // num_children


# ==========================================
# Main Execution
# ==========================================
if __name__ == "__main__":
    # 1. Create the nodes
    while True:
        worker1 = FactoryWorker("Worker 1")
        worker2 = FactoryWorker("Worker 2")
        worker3 = FactoryWorker("Worker 3")
        worker4 = FactoryWorker("Worker 4")

        shift_supervisor_a = Supervisor("Shift Supervisor 1")
        shift_supervisor_b = Supervisor("Shift Supervisor 2")

        team_manager = Supervisor("Team Manager")

        worker5 = FactoryWorker("Worker 5")
        worker6 = FactoryWorker("Worker 6")
        worker7 = FactoryWorker("Worker 7")

        factory_manager = Supervisor("Factory Manager")

        # 2. Build the tree
        shift_supervisor_a.add_subordinate(worker1)
        shift_supervisor_a.add_subordinate(worker2)

        shift_supervisor_b.add_subordinate(worker3)
        shift_supervisor_b.add_subordinate(team_manager)

        team_manager.add_subordinate(worker5)
        team_manager.add_subordinate(worker6)
        team_manager.add_subordinate(worker7)

        factory_manager.add_subordinate(shift_supervisor_a)
        factory_manager.add_subordinate(shift_supervisor_b)


        # 3. Calculate Layout & Show Initial State
        calculate_layout(factory_manager)
        TREE_ROOT = factory_manager
        update_display(1000)  # Pause for a second on the initial gray tree

        # 4. Execute Work
        print("--- Morning Shift Starts ---")
        factory_manager.work()
        print("--- Shift Ended ---")
        time.sleep(1)
        # Keep the window open at the end until a key is pressed
        # print("Press any key in the OpenCV window to exit.")
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()