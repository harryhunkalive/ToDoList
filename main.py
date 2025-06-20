import csv
import os
from datetime import datetime, date, timedelta
from colorama import init, Fore, Back, Style

# Initialize colorama for Windows compatibility
init(autoreset=True)

class TodoManager:
    """
    A comprehensive To-Do List Manager that handles task creation, modification,
    and tracking with CSV file persistence.
    """
    
    def __init__(self, filename='tasks.csv'):
        """
        Initialize the TodoManager with a CSV file for data persistence.
        
        Args:
            filename (str): Name of the CSV file to store tasks
        """
        self.filename = filename
        self.fieldnames = ['id', 'title', 'description', 'due_date', 'priority', 
                          'status', 'created_at', 'completed_at']
        self.tasks = self.load_tasks()
        self.update_overdue_tasks()
    
    def load_tasks(self):
        """
        Load tasks from CSV file. Creates a new file if it doesn't exist.
        
        Returns:
            list: List of task dictionaries
        """
        if not os.path.exists(self.filename):
            # Create file with headers if it doesn't exist
            with open(self.filename, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
            return []
        
        tasks = []
        try:
            with open(self.filename, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert ID to integer for proper sorting
                    row['id'] = int(row['id'])
                    # Handle None values for completed_at field
                    if row['completed_at'] == '':
                        row['completed_at'] = None
                    tasks.append(row)
        except Exception as e:
            print(f"{Fore.RED}Error reading tasks file: {e}")
            return []
        
        return tasks
    
    def save_tasks(self):
        """
        Save all tasks to the CSV file.
        Converts None values to empty strings for CSV compatibility.
        """
        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            for task in self.tasks:
                # Create a copy to avoid modifying the original
                task_copy = task.copy()
                if task_copy['completed_at'] is None:
                    task_copy['completed_at'] = ''
                writer.writerow(task_copy)
    
    def get_next_id(self):
        """
        Generate the next available ID for a new task.
        
        Returns:
            int: Next available ID
        """
        if not self.tasks:
            return 1
        return max(task['id'] for task in self.tasks) + 1
    
    def update_overdue_tasks(self):
        """
        Check all tasks and update their status to 'Overdue' if the due date has passed.
        Only updates tasks that are not already completed.
        """
        today = date.today()
        updated = False
        
        for task in self.tasks:
            # Skip completed tasks
            if task['status'] != 'Completed':
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if due_date < today:
                    # Mark as overdue if past due date
                    if task['status'] != 'Overdue':
                        task['status'] = 'Overdue'
                        updated = True
                elif task['status'] == 'Overdue':
                    # Reset status if date was changed to future
                    task['status'] = 'Pending'
                    updated = True
        
        # Save only if changes were made
        if updated:
            self.save_tasks()
    
    def print_header(self, text):
        """
        Print a styled header with consistent formatting.
        
        Args:
            text (str): Header text to display
        """
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{'='*3} {Fore.WHITE}{Style.BRIGHT}{text.center(52)} {Fore.CYAN}{'='*3}")
        print(f"{Fore.CYAN}{'='*60}")
    
    def add_task(self):
        """
        Interactive function to add a new task.
        Validates input and ensures due dates are not in the past.
        """
        self.print_header("ADD NEW TASK")
        
        # Get task title (required)
        title = input(f"{Fore.YELLOW}Enter task title: {Style.RESET_ALL}").strip()
        if not title:
            print(f"{Fore.RED}Error: Title cannot be empty!")
            return
        
        # Get task description (optional)
        description = input(f"{Fore.YELLOW}Enter task description (optional): {Style.RESET_ALL}").strip()
        
        # Get and validate due date
        today = date.today()
        print(f"{Fore.BLUE}Today's date: {today.strftime('%Y-%m-%d')}")
        
        while True:
            due_date_str = input(f"{Fore.YELLOW}Enter due date (YYYY-MM-DD): {Style.RESET_ALL}").strip()
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
                # Validate date is not in the past
                if due_date < today:
                    print(f"{Fore.RED}Error: Due date cannot be in the past! Please enter today or a future date.")
                    continue
                
                # Show helpful feedback about the due date
                days_until = (due_date - today).days
                if days_until == 0:
                    print(f"{Fore.YELLOW}Due today!")
                elif days_until == 1:
                    print(f"{Fore.GREEN}Due tomorrow!")
                else:
                    print(f"{Fore.GREEN}Due in {days_until} days.")
                break
            except ValueError:
                print(f"{Fore.RED}Invalid date format! Please use YYYY-MM-DD")
        
        # Get priority level
        print(f"{Fore.YELLOW}Select priority:")
        print(f"  {Fore.RED}H{Fore.YELLOW} - High")
        print(f"  {Fore.YELLOW}M{Fore.YELLOW} - Medium")
        print(f"  {Fore.GREEN}L{Fore.YELLOW} - Low")
        
        while True:
            priority = input(f"{Fore.YELLOW}Enter priority (H/M/L): {Style.RESET_ALL}").strip().upper()
            priority_map = {'H': 'High', 'M': 'Medium', 'L': 'Low'}
            if priority in priority_map:
                priority = priority_map[priority]
                break
            print(f"{Fore.RED}Invalid priority! Please enter H, M, or L")
        
        # Create new task
        task = {
            'id': self.get_next_id(),
            'title': title,
            'description': description,
            'due_date': due_date_str,
            'priority': priority,
            'status': 'Pending',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'completed_at': None
        }
        
        # Add task and save
        self.tasks.append(task)
        self.save_tasks()
        print(f"{Fore.GREEN}{Style.BRIGHT}\n✓ Task added successfully! (ID: {task['id']})")
    
    def mark_completed(self):
        """
        Mark a task as completed by its ID.
        Shows pending tasks for easy reference.
        """
        self.print_header("MARK TASK AS COMPLETED")
        
        # Show available tasks to complete
        pending_tasks = [t for t in self.tasks if t['status'] != 'Completed']
        if not pending_tasks:
            print(f"{Fore.YELLOW}No pending tasks to complete!")
            return
            
        print(f"\n{Fore.CYAN}Pending/Overdue tasks:")
        for task in pending_tasks:
            status_color = Fore.RED if task['status'] == 'Overdue' else Fore.YELLOW
            print(f"  ID: {Fore.WHITE}{task['id']:<3} {status_color}{task['title']}")
        
        # Get task ID to complete
        task_id = input(f"\n{Fore.YELLOW}Enter task ID to mark as completed: {Style.RESET_ALL}").strip()
        try:
            task_id = int(task_id)
        except ValueError:
            print(f"{Fore.RED}Error: Invalid task ID!")
            return
        
        # Find and update task
        task = self.find_task_by_id(task_id)
        if not task:
            print(f"{Fore.RED}Error: Task with ID {task_id} not found!")
            return
        
        if task['status'] == 'Completed':
            print(f"{Fore.YELLOW}Task is already completed!")
            return
        
        # Mark as completed
        task['status'] = 'Completed'
        task['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_tasks()
        print(f"{Fore.GREEN}{Style.BRIGHT}✓ Task '{task['title']}' marked as completed!")
    
    def delete_task(self):
        """
        Delete a task after confirmation.
        Shows all tasks for reference before deletion.
        """
        self.print_header("DELETE TASK")
        
        if not self.tasks:
            print(f"{Fore.YELLOW}No tasks to delete!")
            return
            
        # Display all tasks for reference
        print(f"\n{Fore.CYAN}Current tasks:")
        for task in self.tasks:
            status_color = (Fore.GREEN if task['status'] == 'Completed' 
                          else Fore.RED if task['status'] == 'Overdue' 
                          else Fore.YELLOW)
            print(f"  ID: {Fore.WHITE}{task['id']:<3} {status_color}{task['title']}")
        
        # Get task ID to delete
        task_id = input(f"\n{Fore.YELLOW}Enter task ID to delete: {Style.RESET_ALL}").strip()
        try:
            task_id = int(task_id)
        except ValueError:
            print(f"{Fore.RED}Error: Invalid task ID!")
            return
        
        # Find task
        task = self.find_task_by_id(task_id)
        if not task:
            print(f"{Fore.RED}Error: Task with ID {task_id} not found!")
            return
        
        # Show task details and confirm deletion
        print(f"\n{Fore.YELLOW}Task to delete:")
        print(f"  Title: {Fore.WHITE}{task['title']}")
        print(f"  Due date: {Fore.WHITE}{task['due_date']}")
        print(f"  Status: {Fore.WHITE}{task['status']}")
        
        confirm = input(f"\n{Fore.RED}Are you sure you want to delete this task? (yes/no): {Style.RESET_ALL}").strip().lower()
        if confirm == 'yes':
            self.tasks.remove(task)
            self.save_tasks()
            print(f"{Fore.GREEN}{Style.BRIGHT}✓ Task deleted successfully!")
        else:
            print(f"{Fore.YELLOW}Deletion cancelled.")
    
    def find_task_by_id(self, task_id):
        """
        Find a task by its ID.
        
        Args:
            task_id (int): The ID of the task to find
            
        Returns:
            dict or None: Task dictionary if found, None otherwise
        """
        for task in self.tasks:
            if task['id'] == task_id:
                return task
        return None
    
    def view_all_tasks(self):
        """
        Display all tasks sorted by priority and overdue status.
        """
        self.print_header("ALL TASKS")
        
        if not self.tasks:
            print(f"{Fore.YELLOW}No tasks found! Start by adding a new task.")
            return
        
        # Update overdue status before displaying
        self.update_overdue_tasks()
        
        # Sort tasks: Overdue first, then by priority, then by due date
        priority_order = {'High': 0, 'Medium': 1, 'Low': 2}
        sorted_tasks = sorted(self.tasks, 
                            key=lambda x: (
                                0 if x['status'] == 'Overdue' else 1,
                                priority_order.get(x['priority'], 3),
                                x['due_date']
                            ))
        
        self.display_tasks(sorted_tasks)
    
    def display_tasks(self, tasks):
        """
        Display tasks in a formatted table with proper alignment.
        
        Args:
            tasks (list): List of task dictionaries to display
        """
        if not tasks:
            print(f"{Fore.YELLOW}No tasks to display!")
            return
        
        # Always check for overdue tasks before displaying
        self.update_overdue_tasks()
        
        # Define column widths for proper alignment
        col_widths = {
            'id': 6,
            'title': 30,
            'due_date': 22,
            'priority': 10,
            'status': 18,
            'created': 20
        }
        
        # Calculate total width
        total_width = sum(col_widths.values()) + 5  # 5 for spacing between columns
        
        # Print header
        print(f"\n{Fore.CYAN}" + "-" * total_width)
        print(f"{Fore.WHITE}{Style.BRIGHT}"
              f"{'ID':<{col_widths['id']}}"
              f"{'Title':<{col_widths['title']}}"
              f"{'Due Date':<{col_widths['due_date']}}"
              f"{'Priority':<{col_widths['priority']}}"
              f"{'Status':<{col_widths['status']}}"
              f"{'Created':<{col_widths['created']}}")
        print(f"{Fore.CYAN}" + "-" * total_width)
        
        # Display each task
        for task in tasks:
            # Determine status display and color
            if task['status'] == 'Overdue':
                status_color = Fore.RED
                status_display = f"[!] {task['status']}"
            elif task['status'] == 'Completed':
                status_color = Fore.GREEN
                status_display = f"[✓] {task['status']}"
            else:
                status_color = Fore.YELLOW
                status_display = f"[-] {task['status']}"
            
            # Set priority colors
            priority_colors = {
                'High': Fore.RED,
                'Medium': Fore.YELLOW,
                'Low': Fore.GREEN
            }
            priority_color = priority_colors.get(task['priority'], Fore.WHITE)
            
            # Truncate title if too long
            title_display = task['title']
            if len(title_display) > col_widths['title'] - 3:
                title_display = title_display[:col_widths['title']-6] + '...'
            
            # Calculate days until due/overdue
            due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
            today = date.today()
            days_diff = (due_date - today).days
            
            # Format due date display with days remaining/overdue
            if task['status'] == 'Completed':
                date_display = task['due_date']
            elif days_diff < 0:
                date_display = f"{task['due_date']} ({abs(days_diff)}d late)"
            elif days_diff == 0:
                date_display = f"{task['due_date']} (Today!)"
            elif days_diff == 1:
                date_display = f"{task['due_date']} (Tomorrow)"
            else:
                date_display = f"{task['due_date']} ({days_diff}d left)"
            
            # Print task row with proper alignment
            print(f"{Fore.WHITE}{str(task['id']):<{col_widths['id']}}"
                  f"{Fore.WHITE}{title_display:<{col_widths['title']}}"
                  f"{Fore.CYAN}{date_display:<{col_widths['due_date']}}"
                  f"{priority_color}{task['priority']:<{col_widths['priority']}}"
                  f"{status_color}{status_display:<{col_widths['status']}}"
                  f"{Fore.BLUE}{task['created_at']:<{col_widths['created']}}")
        
        print(f"{Fore.CYAN}" + "-" * total_width)
        
        # Display summary statistics
        pending = len([t for t in tasks if t['status'] == 'Pending'])
        completed = len([t for t in tasks if t['status'] == 'Completed'])
        overdue = len([t for t in tasks if t['status'] == 'Overdue'])
        
        print(f"\n{Fore.WHITE}{Style.BRIGHT}Summary: "
              f"{Fore.YELLOW}Pending: {pending}  "
              f"{Fore.GREEN}Completed: {completed}  "
              f"{Fore.RED}Overdue: {overdue}  "
              f"{Fore.CYAN}Total: {len(tasks)}")
    
    def filter_tasks(self):
        """
        Filter tasks by various criteria such as status, priority, or due date.
        """
        self.print_header("FILTER TASKS")
        
        # Display filter options
        print(f"{Fore.YELLOW}1. {Fore.WHITE}Pending tasks")
        print(f"{Fore.GREEN}2. {Fore.WHITE}Completed tasks")
        print(f"{Fore.CYAN}3. {Fore.WHITE}Tasks due today or tomorrow")
        print(f"{Fore.RED}4. {Fore.WHITE}Overdue tasks")
        print(f"{Fore.MAGENTA}5. {Fore.WHITE}High priority tasks")
        
        choice = input(f"\n{Fore.YELLOW}Select filter option (1-5): {Style.RESET_ALL}").strip()
        
        # Update overdue status before filtering
        self.update_overdue_tasks()
        
        filtered_tasks = []
        filter_name = ""
        
        # Apply selected filter
        if choice == '1':
            filtered_tasks = [t for t in self.tasks if t['status'] == 'Pending']
            filter_name = "Pending Tasks"
        elif choice == '2':
            filtered_tasks = [t for t in self.tasks if t['status'] == 'Completed']
            filter_name = "Completed Tasks"
        elif choice == '3':
            today = date.today()
            tomorrow = today + timedelta(days=1)
            filtered_tasks = []
            for task in self.tasks:
                task_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if task_date == today or task_date == tomorrow:
                    filtered_tasks.append(task)
            filter_name = "Tasks Due Today or Tomorrow"
        elif choice == '4':
            filtered_tasks = [t for t in self.tasks if t['status'] == 'Overdue']
            filter_name = "Overdue Tasks"
        elif choice == '5':
            filtered_tasks = [t for t in self.tasks if t['priority'] == 'High']
            filter_name = "High Priority Tasks"
        else:
            print(f"{Fore.RED}Invalid choice!")
            return
        
        # Display filtered results
        self.print_header(filter_name.upper())
        self.display_tasks(filtered_tasks)
    
    def search_tasks(self):
        """
        Search tasks by keyword in title or description.
        """
        self.print_header("SEARCH TASKS")
        
        keyword = input(f"{Fore.YELLOW}Enter search keyword: {Style.RESET_ALL}").strip().lower()
        
        if not keyword:
            print(f"{Fore.RED}Error: Search keyword cannot be empty!")
            return
        
        # Search in title and description
        matching_tasks = []
        for task in self.tasks:
            if (keyword in task['title'].lower() or 
                keyword in task['description'].lower()):
                matching_tasks.append(task)
        
        # Display results
        self.print_header(f"SEARCH RESULTS FOR '{keyword.upper()}'")
        
        if not matching_tasks:
            print(f"{Fore.YELLOW}No tasks found matching '{keyword}'")
        else:
            self.display_tasks(matching_tasks)
    
    def export_summary(self):
        """
        Export a detailed task summary to a text file.
        Includes statistics, task details by priority, and upcoming tasks.
        """
        self.print_header("EXPORT SUMMARY")
        
        # Get filename from user
        filename = input(f"{Fore.YELLOW}Enter filename for export (default: task_summary.txt): {Style.RESET_ALL}").strip()
        if not filename:
            filename = "task_summary.txt"
        
        # Ensure .txt extension
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                f.write("TASK SUMMARY REPORT\n")
                f.write("=" * 50 + "\n")
                f.write(f"Report generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Update overdue tasks before generating report
                self.update_overdue_tasks()
                
                # Calculate statistics
                total_tasks = len(self.tasks)
                pending_tasks = len([t for t in self.tasks if t['status'] == 'Pending'])
                completed_tasks = len([t for t in self.tasks if t['status'] == 'Completed'])
                overdue_tasks = len([t for t in self.tasks if t['status'] == 'Overdue'])
                
                # Write statistics
                f.write("STATISTICS:\n")
                f.write(f"Total Tasks: {total_tasks}\n")
                f.write(f"Pending: {pending_tasks}\n")
                f.write(f"Completed: {completed_tasks}\n")
                f.write(f"Overdue: {overdue_tasks}\n\n")
                
                # Write tasks by priority
                for priority in ['High', 'Medium', 'Low']:
                    priority_tasks = [t for t in self.tasks if t['priority'] == priority]
                    if priority_tasks:
                        f.write(f"\n{priority.upper()} PRIORITY TASKS:\n")
                        f.write("-" * 50 + "\n")
                        for task in priority_tasks:
                            status = f"[{task['status']}]"
                            f.write(f"{status:<15} {task['title']:<30} Due: {task['due_date']}\n")
                            if task['description']:
                                f.write(f"{'':>15} Description: {task['description']}\n")
                
                # Write upcoming tasks section
                f.write("\n\nUPCOMING TASKS (Next 7 days):\n")
                f.write("-" * 50 + "\n")
                today = date.today()
                week_later = today + timedelta(days=7)
                upcoming = []
                
                # Find upcoming tasks
                for task in self.tasks:
                    if task['status'] == 'Pending':
                        task_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                        if today <= task_date <= week_later:
                            upcoming.append(task)
                
                # Write upcoming tasks
                if upcoming:
                    for task in sorted(upcoming, key=lambda x: x['due_date']):
                        f.write(f"{task['due_date']} - {task['title']} [{task['priority']}]\n")
                else:
                    f.write("No upcoming tasks in the next 7 days.\n")
                
            print(f"{Fore.GREEN}{Style.BRIGHT}✓ Summary exported successfully to {filename}")
            
            # Offer to open the file
            open_file = input(f"\n{Fore.YELLOW}Do you want to open the file? (yes/no): {Style.RESET_ALL}").strip().lower()
            if open_file == 'yes':
                # Open file with default system program
                os.system(f'start {filename}' if os.name == 'nt' else f'open {filename}')
                
        except Exception as e:
            print(f"{Fore.RED}Error exporting summary: {str(e)}")
    
    def show_dashboard(self):
        """
        Display a quick dashboard with task statistics and today's tasks.
        Provides an at-a-glance view of task status and priorities.
        """
        self.print_header("TASK DASHBOARD")
        
        # Update overdue tasks
        self.update_overdue_tasks()
        
        # Calculate statistics
        total = len(self.tasks)
        if total == 0:
            print(f"{Fore.YELLOW}No tasks yet! Start by adding your first task.")
            return
        
        # Count tasks by status
        pending = len([t for t in self.tasks if t['status'] == 'Pending'])
        completed = len([t for t in self.tasks if t['status'] == 'Completed'])
        overdue = len([t for t in self.tasks if t['status'] == 'Overdue'])
        
        # Count active tasks by priority
        high = len([t for t in self.tasks if t['priority'] == 'High' and t['status'] != 'Completed'])
        medium = len([t for t in self.tasks if t['priority'] == 'Medium' and t['status'] != 'Completed'])
        low = len([t for t in self.tasks if t['priority'] == 'Low' and t['status'] != 'Completed'])
        
        # Find today's tasks
        today = date.today()
        today_tasks = []
        for task in self.tasks:
            if task['status'] != 'Completed':
                task_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if task_date == today:
                    today_tasks.append(task)
        
        # Display overview section
        print(f"\n{Fore.WHITE}{Style.BRIGHT}📊 OVERVIEW")
        print(f"{Fore.CYAN}{'─' * 40}")
        
        # Task status breakdown
        print(f"{Fore.WHITE}Total Tasks: {Fore.CYAN}{total}")
        print(f"{Fore.YELLOW}⏳ Pending: {pending}")
        print(f"{Fore.GREEN}✓ Completed: {completed} ({completed/total*100:.1f}%)")
        print(f"{Fore.RED}⚠ Overdue: {overdue}")
        
        # Priority breakdown
        print(f"\n{Fore.WHITE}{Style.BRIGHT}🎯 ACTIVE TASKS BY PRIORITY")
        print(f"{Fore.CYAN}{'─' * 40}")
        print(f"{Fore.RED}🔴 High: {high}")
        print(f"{Fore.YELLOW}🟡 Medium: {medium}")
        print(f"{Fore.GREEN}🟢 Low: {low}")
        
        # Today's tasks
        print(f"\n{Fore.WHITE}{Style.BRIGHT}📅 TODAY'S TASKS")
        print(f"{Fore.CYAN}{'─' * 40}")
        if today_tasks:
            for task in today_tasks:
                priority_icon = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}.get(task['priority'], '⚪')
                print(f"{priority_icon} {task['title']}")
        else:
            print(f"{Fore.GREEN}No tasks due today! 🎉")
    
    def run(self):
        """
        Main application loop.
        Displays menu and handles user input until exit is selected.
        """
        # Clear screen and show welcome message
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{'='*3} {Fore.WHITE}{Style.BRIGHT}{'SMART TO-DO LIST MANAGER'.center(52)} {Fore.CYAN}{'='*3}")
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.YELLOW}Welcome! Let's get organized and productive! 🚀")
        
        # Main menu loop
        while True:
            # Display menu options
            print(f"\n{Fore.CYAN}=== MAIN MENU ===")
            print(f"{Fore.WHITE}1. {Fore.YELLOW}📝 Add Task")
            print(f"{Fore.WHITE}2. {Fore.CYAN}📋 View All Tasks")
            print(f"{Fore.WHITE}3. {Fore.GREEN}✓ Mark Task as Completed")
            print(f"{Fore.WHITE}4. {Fore.RED}🗑️  Delete Task")
            print(f"{Fore.WHITE}5. {Fore.MAGENTA}🔍 Filter Tasks")
            print(f"{Fore.WHITE}6. {Fore.BLUE}🔎 Search Tasks")
            print(f"{Fore.WHITE}7. {Fore.YELLOW}📊 Dashboard")
            print(f"{Fore.WHITE}8. {Fore.GREEN}💾 Export Summary")
            print(f"{Fore.WHITE}9. {Fore.RED}🚪 Exit")
            
            # Get user choice
            choice = input(f"\n{Fore.YELLOW}Select an option (1-9): {Style.RESET_ALL}").strip()
            
            # Process user choice
            if choice == '1':
                self.add_task()
            elif choice == '2':
                self.view_all_tasks()
            elif choice == '3':
                self.mark_completed()
            elif choice == '4':
                self.delete_task()
            elif choice == '5':
                self.filter_tasks()
            elif choice == '6':
                self.search_tasks()
            elif choice == '7':
                self.show_dashboard()
            elif choice == '8':
                self.export_summary()
            elif choice == '9':
                # Exit program
                print(f"\n{Fore.GREEN}{Style.BRIGHT}Thank you for using Smart To-Do List Manager!")
                print(f"{Fore.YELLOW}Stay organized and productive! Goodbye! 👋")
                print(f"{Fore.CYAN}Created by Harryhunkalive 😊")
                break
            else:
                print(f"\n{Fore.RED}Invalid choice! Please select a valid option (1-9)")
            
            # Pause before showing menu again
            input(f"\n{Fore.CYAN}Press Enter to continue...{Style.RESET_ALL}")
            # Clear screen for better user experience
            os.system('cls' if os.name == 'nt' else 'clear')


# Main program entry point
if __name__ == "__main__":
    try:
        # Create and run the todo manager
        todo_manager = TodoManager()
        todo_manager.run()
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        print(f"\n\n{Fore.YELLOW}Program interrupted. Goodbye! 👋")
    except Exception as e:
        # Handle any unexpected errors
        print(f"\n{Fore.RED}An unexpected error occurred: {str(e)}")
        print(f"{Fore.YELLOW}Please restart the program.")