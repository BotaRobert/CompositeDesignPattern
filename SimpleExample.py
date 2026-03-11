import time
from abc import ABC, abstractmethod


class Employee(ABC):
    """The Component base class for all employees."""

    def __init__(self, emp_id: str):
        self.emp_id = emp_id

    @abstractmethod
    def work(self):
        """Abstract method to be implemented by leaves and composites."""
        pass


class FactoryWorker(Employee):
    """The Leaf class representing workers at the bottom of the hierarchy."""

    # Static counter shared across all FactoryWorker instances
    total_products_built = 0

    def work(self):
        # Simulate the time it takes to build a product
        time.sleep(1.0)

        FactoryWorker.total_products_built += 1
        print(
            f"  [🛠️] Worker {self.emp_id} has built a product. (Total factory products: {FactoryWorker.total_products_built})")


class Supervisor(Employee):
    """The Composite class representing employees who manage others."""

    def __init__(self, emp_id: str):
        super().__init__(emp_id)
        self.subordinates = []

    def add_subordinate(self, employee: Employee):
        self.subordinates.append(employee)

    def remove_subordinate(self, employee: Employee):
        self.subordinates.remove(employee)

    def work(self):
        # Gather the IDs of the direct subordinates for the print statement
        subordinate_ids = [sub.emp_id for sub in self.subordinates]

        # Simulate the time it takes to organize and assign work
        time.sleep(0.5)
        print(f"[📋] Supervisor {self.emp_id} has given work to its subordinates: {subordinate_ids}")

        # Delegate work down the tree
        for subordinate in self.subordinates:
            subordinate.work()



if __name__ == "__main__":
    worker1 = FactoryWorker("W-001")
    worker2 = FactoryWorker("W-002")
    worker3 = FactoryWorker("W-003")
    worker4 = FactoryWorker("W-004")

    team_manager = Supervisor("T-100")

    worker5 = FactoryWorker("W-005")
    worker6 = FactoryWorker("W-006")
    worker7 = FactoryWorker("W-007")

    factory_manager = Supervisor("M-999")

    shift_supervisor_a = Supervisor("S-100")
    shift_supervisor_b = Supervisor("S-101")

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


    print("--- Morning Shift Starts ---")
    factory_manager.work()
    print("--- Shift Ended ---")