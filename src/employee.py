import datetime

class ValidationError(Exception):
    pass

class AttendanceError(Exception):
    pass

class Employee():
    """ A class to represent an employee of the company.

    This class manages the employee's personal details like unique ID, name
    salary, date hired, contact info and active status.

    Parameters
    ----------
    id : int or str
        The unique identifier of the employee.
    name : str
        The name of the employee.
    role : str
        The position occupied by the employee within the company.
    salary : float
        The amount received by the employee monthly.
    hire_date : datetime.date
        The date the employee was hired.
    contact_info : dict
        The contact's information, e.g., {'email': '...', 'phone': '...'}.
    active : bool, optional
        The employment status of the employee. Defaults to True.
    attendance_info : list
        The attendance records of employees.
    leave_requests : list
        The leave requests of employees.
    meta : dict, optional
        For miscellaneous metadata.

    Attributes
    ----------
    id : int or str
        The unique identifier of the employee.
    name : str
        The name of the employee.
    role : str
        The position occupied by the employee within the company.
    salary : float
        The amount received by the employee monthly.
    hire_date : datetime
        The date the employee was hired. Stored as str.
    contact_info : dict
        The contact's information.
    active : bool
        The employment status of the employee.
    attendance_info : list
        The attendance records of employees; each record is a simple dict with keys 
        "clock_in" and optionally "clock_out" (timestamps stored as ISO strings).
    leave_requests : list
        The leave requests of employees with leave objects (each with id, 
        start_date, end_date, reason, status).
    meta : dict
        For miscellaneous metadata.
    """
    def __init__( self, id, name, role, salary, hire_date, contact_info, active, 
                 attendance_info, leave_requests, meta ):
        self.id = id
        self.name = name
        self.role = role
        self.salary = salary
        self.hire_date = hire_date
        self.contact_info = contact_info
        self.active = active
        self.attendance_info = attendance_info
        self.leave_requests = leave_requests
        self.meta = meta
        
        # Validate every attribute to ensure they meet the requirements.
        self.validate()

    def get_details( self ):
        """
        Returns a serializable dictionary representation of the employee.

        This method converts all attributes of the Employee object into a dictionary
        with basic Python types, suitable for serialization (e.g., to JSON).
        Dates are converted to ISO 8601 strings.

        Returns
        -------
        dict
            A dictionary containing all employee attributes.
        """
        details = {
            "id" : self.id,
            "name" : self.name,
            "role" : self.role,
            "salary" : self.salary,
            "hire_date" : str(self.hire_date),
            "contact_info" : self.contact_info,
            "active" : self.active, 
            "attendance_info" : self.attendance_info,
            "leave_requests" : self.leave_requests,
            "meta" : self.meta
        }
        return details
    
    def update_salary( self, new_salary: (int, float) ): # type: ignore
        if new_salary > 0:
            self.salary = new_salary
        else:
            raise ValidationError("Salary must be a positive number.")
    
    def update_contact( self, new_contact ):
        """
        Validates and updates the employee's contact information.

        This method validates the fields in `new_contact` and merges them
        with the existing `contact_info` dictionary. The 'phone' field is
        validated to ensure it contains only numeric characters.

        Parameters
        ----------
        new_contact : dict
            A dictionary containing the new contact information. Expected keys
            are 'phone' and 'email' (optional).

        Returns
        -------
        bool
            True if the contact information was successfully updated.

        Raises
        ------
        ValidationError
            If the 'phone' field is not a string of digits, or if the
            input is not a dictionary.
        """
        if not isinstance( new_contact, dict ):
            raise ValidationError("New contact info must be a dictionary.")
        
        if "phone" in new_contact and not str(new_contact["phone"]).isdigit():
            raise ValidationError("Phone number must contain only digits.")
        
        self.contact_info.update(new_contact)
        return True
    
    def clock_in( self, timestamp=None ):
        # Get the current time if no timestamp is provided
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()

        # Check for an existing open attendance entry
        if self.attendance_info and "clock_out" not in self.attendance_info[-1]:
            raise AttendanceError("Already clocked in. Cannot clock in again without clocking out.")
        
        # Add a new clock in list to the attendance entry
        new_entry = {"clock_in" : timestamp}
        self.attendance_info.append(new_entry)

        return True
    
    def clock_out( self, timestamp=None ):
        # Get the current time if no timestamp is provided
        if timestamp is None:
            timestamp = datetime.datetime.now().isoformat()

        # Check for an existing open attendance entry to clock out from
        if not self.attendance_info or "clock_out" in self.attendance_info[-1]:
            raise AttendanceError("No active clock in to clock out from.")
        
        # Find the most recent entry and add the clock-out time
        self.attendance_info[-1]["clock_out"] = timestamp

        # Calculate duration
        start_time_str = self.attendance_info[-1]["clock_in"]
        end_time_str = self.attendance_info[-1]["clock_out"]
        
        start_time = datetime.datetime.fromisoformat(start_time_str)
        end_time = datetime.datetime.fromisoformat(end_time_str)
        
        duration = end_time - start_time
        duration_minutes = duration.total_seconds() / 60
        
        self.attendance_info[-1]["duration_minutes"] = round(duration_minutes, 2)

        return True
    
    def request_leave( self, start_date, end_date, reason ):
        # Basic validation: start date must not be after end date
        if start_date > end_date:
            raise ValidationError("Start date can not be after end date.")
        
        # Create a unique ID for the leave request
        request_id = datetime.datetime.now().strftime(r"%Y-%m-%d,%H:%M:%S")

        # Create new leave requests dictionary
        new_request = {
            "id" : request_id,
            "start_date" : str(start_date),
            "end_date" : str(end_date),
            "reason" : reason,
            "status" : "pending"
        }

        # Add new request to the leave request dictionary
        self.leave_requests.append(new_request)

        # Return the ID of the new request
        return request_id

    def to_dict(self):
        # Creates a dictionary from the employee attribute
        employee_dict = self.__dict__.copy()

        # Converts the hire_date to astring for easy saving 
        # datetime objects can't be saved directly to a file like JSON. 
        # converts the date into a simple string format that is universally understood.
        if isinstance(employee_dict["hire_date"], datetime.datetime):
            employee_dict["hire_date"] = employee_dict["hire_date"].isoformat()

        return employee_dict

    @classmethod
    def from_dict(cls, employee_dict):
        # Creates an Employee object from a dictionary
        # The `**` before employee_dict unpacks the dictionary into arguments
        # for the Employee class constructor (__init__)
        return cls(**employee_dict)

    def activate( self ):
        # Sets the employees active status to True
        self.active = True

    def deactivate( self, reason=None ):
        # Sets the employees active status to False
        self.active = False
        if reason:
            self.meta["termination_reason"] = reason

    def validate(self):
        errors = []

        # Validate id
        if not isinstance(self.id, (int, str)) or isinstance(self.id, str) and not self.id.strip():
            errors.append("Employee ID must be a non-empty string or integer ")
        
        # Validate that the salary is not negative
        if not isinstance(self.salary, (int, float)) or self.salary < 0:
            errors.append("Salary must be a non-negative number.")
        
        # Validate that the name is not empty
        if not isinstance(self.name, str) and not self.name.strip():
            errors.append("Name must be a non-empty string.")
        
        # Validate role
        if not isinstance(self.role, str) and not self.role.strip():
            errors.append("Employee role must be a non-empty string")
                        
        # Validate that hire date is a datetime or a string
        if not isinstance(self.hire_date, (datetime.datetime, str)):
            raise ValidationError("Hire date must be a datetime object or string.")
        
        # Validate contact info
        if not isinstance(self.contact_info, dict):
            errors.append("Contanct information must be a dictionary")
        if "phone" in self.contact_info and not str(self.contact_info["phone"]).isdigit():
            errors.append("Phone number in contact info must contain only digits.")
        if "email" in self.contact_info and ("@" not in self.contact_info and not self.contact_info["email"]):
            errors.append("Email in contact info must be valid.")
        
        # Validate active
        if not isinstance(self.active, bool):
            errors.append("Active status must be boolean.")
        
        # Validate attendance info
        if not isinstance(self.attendance_info, list):
            errors.append("Attendance info must be a list.")
        
        # Validate leave request 
        if not isinstance(self.leave_requests, list):
            errors.append("Leave request info must be a list.")
        
        # Validate meta
        if not isinstance(self.meta, dict):
            errors.append("Meta must be a dictionary.")

        # After checking everything, if there are any errors, raise a single exception
        if errors:
            error_message = "\n".join(errors)
            raise ValidationError(error_message)
        


# MANUAL TESTING FOR THE IMPLEMENTATION OF EMPLOYEE
print("---- Starting Manual Test ----")

# Create a valid datetime for hire_date
hire_date = datetime.datetime(2025, 9, 13)

# Instantiate the Employee object with all required (10) arguments
emp = Employee(
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

print("\n1. Validating update contact with a valid and invalid contact...")
try:
    emp.update_contact({"phone": "+2348061985820"})
    print("Contact updated successfully.")
    emp.update_contact({"phone": "08061985820"})
except ValidationError as e:
    print(f"Correctly caught expected error: {e}")
print("Contact updated successfully.")
print("Contact info updated: ", emp.contact_info)

print("\n2. Validating clock in/out and checking updated attendance list...")
emp.clock_in()
print("Successfully clocked in")
emp.clock_out()
print("Successfully clocked out")
print("Attendance information: ", emp.attendance_info)

print("\n3. Validating request_leave call and confriming if leave_requests " \
"list contains expected entries...")
emp.request_leave("2025-10-10", "2026-1-10", "Family emergencies!")
print("Leave request successful.")
print("Leave requests: ", emp.leave_requests)

print("\n4. Validating to_dict and from_dict")
# Create the dictionary from the existing employee object
employee_data_dict = emp.to_dict()
print("DIctionary successfully created from the existing employee object.")
# Use the classmethod to create a new employee object from that dictionary
new_emp = Employee.from_dict(employee_data_dict)
print("New employee objest successfully created.")
print("New employee object's name: ", new_emp.name)

print("\n5. Validating error and behavor...")
print("Clock in twice in a row")
try:
    emp.clock_in()
    emp.clock_in()
except AttendanceError as e:
    print(f"Correctly caught an expected error {e}")

print("\n Requesing leave where start_date > end_date...")
try:
    emp.request_leave("2025-10-10", "2024-1-10", "Running stomach")
except ValidationError as e:
    print(f"Correctly caught an expected error {e}")

print("\n Passing negative salary...")
try:
    emp.update_salary(-120000)
except ValidationError as e:
    print(f"Caught an expected error {e}")
print("Passing a list of contact and non numerical phone number...")
try:
    emp.update_contact([+2348123456789, "somebody.com"])
except ValidationError as e:
    print(f"Caught an expected error {e}")
try:
    emp.update_contact({"phone":"+234ABCDEFGHIJ"})
except ValidationError as e:
    print(f"Caught an expected error {e}")
print("\n--- Manual Tests Complete ---")