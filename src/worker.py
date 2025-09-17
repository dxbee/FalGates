from employee import Employee, ValidationError, AttendanceError
import datetime
import time

class Worker(Employee):
    """ 
    A class to represent employees who operate machines and contribute to production.

    This class adds worker-specific fields and behaviors on top of the base Employee class.
    """
    def __init__( self, id, name, role, salary, hire_date, contact_info, active, 
                 attendance_info, leave_requests, meta, assigned_unit_id = None, shift = None, 
                 skills = None, current_task = None, productivity_records = None, wage_type = "salary" ):
        
        # Call the __init__ method of the super (parent) class (Employee)
        super().__init__( id, name, role, salary, hire_date, contact_info, active, 
                 attendance_info, leave_requests, meta )
        
        # New attributes specif to a Worker
        self.assigned_unit_id = assigned_unit_id
        self.shift = shift
        self.skills = skills if skills is not None else []
        self.current_task = current_task
        self.productivity_records = productivity_records if productivity_records is not None else []
        self.wage_type = wage_type

    def assign_to_unit( self, unit_id: str ):
        """
        Assigns the worker to a production unit.
        
        Parameters
        ----------
        unit_id : str
            The ID of the production unit.
        
        Raises
        ------
        ValidationError
            If the worker is not active.
        """
        # Check if worker is active
        if not self.active:
            raise ValidationError("Cannot assign unit to an inactive worker.")
        self.assign_to_unit_id = unit_id

    def assign_shift( self, shift_label: str ):
        """
        Assigns the worker to a specific shift.
        
        Parameters
        ----------
        shift_label : str
            The label of the shift (e.g., "morning", "night").
        """
        self.shift = shift_label

    def add_skill( self, skill_name: str ):
        """
        Adds a new skill to the worker's skills list, avoiding duplicates.
        
        Parameters
        ----------
        skill_name : str
            The skill to be added.
        """
        # Add a skill if it is not already in the skill list
        if skill_name not in self.skills:
            self.skills.append(skill_name)

    def remove_skills( self, skill_name: str ):
        """
        Removes a skill from the worker's skills list.
        
        Parameters
        ----------
        skill_name : str
            The skill to be removed.
        """
        if skill_name in self.skills:
            self.skills.remove(skill_name)

    def start_task( self, task_info: dict ):
        """
        Starts a new task for the worker.
        
        Parameters
        ----------
        task_info : dict
            A dictionary containing task details (e.g., id, name).
            
        Raises
        ------
        AttendanceError
            If a task is already in progress.
        """
        # Raise an error if current_task is not None
        if self.current_task is not None:
            raise AttendanceError("Already working on a task.")
        
        task_info["start_time"] = datetime.datetime.now().isoformat()
        self.current_task = task_info
        return True
    
    def stop_task( self ):
        """
        Stops the current task, adds it to productivity records, and clears the current task.
        
        Raises
        ------
        AttendanceError
            If no task is currently active.
        """
        if self.current_task is None:
            raise AttendanceError("No active task to stop.")
        
        self.current_task['end_time'] = datetime.datetime.now().isoformat()
        self.productivity_records.append(self.current_task)
        # Clear the current task
        self.current_task = None
        return True
    
    def record_output( self, quantity: (int, float) ): #type: ignore
        """
        Records a new output quantity and returns the cumulative total.
        
        Parameters
        ----------
        quantity : int or float
            The number of items produced.
        
        Returns
        -------
        int or float
            The cumulative total of all recorded outputs.
            
        Raises
        ------
        ValidationError
            If the quantity is not a positive number.
        """
        if quantity <= 0:
            raise ValidationError("Quantity must be a non negative number.")
        
        output_record = {
            "quantity" : quantity,
            "timestamp" : datetime.datetime.now().isoformat()
        }
        self.productivity_records.append(output_record)

        # Return cummutative output
        total_output = sum(item.get('quantity', 0) for item in self.productivity_records)
        return total_output
    
    def to_dict( self ) -> dict:
        """
        Overrides the parent method to include Worker-specific attributes.
        
        Returns
        -------
        dict
            A serializable dictionary representation of the worker.
        """

        # Get dictionary from the parent class, Employee
        data = super.to_dict()
        
        # Add worker specific fields
        data.update({
            "assigned_unit_id" : self.assign_to_unit_id,
            "shift" : self.shift,
            "skills" : self.skills,
            "current_task" : self.current_task,
            "productivity_records" : self.productivity_records,
            "wage_type" : self.wage_type
        })
        return data
    
    @classmethod
    def from_dict( self, employee_dict: dict ):
        """
        Creates a Worker object from a dictionary, including all parent and child attributes.
        
        Parameters
        ----------
        employee_dict : dict
            A dictionary containing the worker's attributes.
        """
        return employee_dict
    

# MANUAL TESTS
print("---- Starting Manual Tests ----")

# Create a worker instance
print("Test #1: Creating a Worker Instance.")
hire_date = datetime.datetime.now().isoformat()
worker = Worker(
    id = "FALGATES0001",
    name = "Edogameh O. Eniola",
    role = "Head of Admin & HR",
    salary = 120000.00,
    hire_date = hire_date, 
    contact_info = {"phone" : "07035136586", "email" : "info@falgates.com"},
    active = True,
    attendance_info = [],
    leave_requests = [],
    meta = {}
)
print("Worker created successfully.")

print("\n2. Verifying inherited Employee method clock in/out...")
worker.clock_in()
# Simulate random work time
time.sleep(1)
print(f"Worker {worker.id} clocked in successfully.")
worker.clock_out()
print(f"Worker {worker.id} has successfully clocked out.")
print("Attendance info: \n", worker.attendance_info)

print("\n3. Assigning worker to and performing task...")
worker.assign_to_unit("Unit-Q")
print("Assigned to Unit-Q.")
worker.assign_shift("Morning")
print("Assigned to Morning Shift.")
worker.add_skill("Machine Operator")
worker.add_skill("Quality Control")
print("Skills added: ", worker.skills)

print("\n4. Starting a task and record some outputs...")
worker.start_task({"id" : "TASK001", "name" : "OPERATING MACHINE X"})
print("Task started.")
worker.record_output(250)
print("Output recorded (250 units). Cumulative total: ", worker.record_output(200))
worker.stop_task()
print("Task stopped.")
print("Productivity record \n:", worker.productivity_records)

print("\n5. Validating error and behavior (starting a second taks while one is in progress)...")
try:
    worker.start_task({"id":"TASK2", "name":"OPERATING MACHINE Y"})
except AttendanceError as e:
    print(f"Correctly caught expected error: {e}")

print("\n6. Edge-case validation (inactive worker)...")
worker.deactivate(reason="Resigned")
try:
    worker.assign_to_unit("Unit-B")
except ValidationError as e:
    print(f"Correctly caught expected error: {e}")

print("\n--- Manual Tests Complete ---")
