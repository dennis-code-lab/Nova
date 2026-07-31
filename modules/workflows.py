from modules import registry
from modules.logger import log_info, log_error

class WorkflowEngine:
    def __init__(self, name):
        self.name = name
        self.steps = []
        self.context = {}

    def add_step(self, service_name, input_key=None, output_key=None, constant_param=None):
        """Appends a functional step definition to the pipeline sequence."""
        self.steps.append({
            "service": service_name,
            "input_key": input_key,
            "output_key": output_key,
            "constant": constant_param
        })
        return self

    def execute(self, initial_input=None):
        """Executes the pipeline sequence sequentially, passing context variables between steps."""
        log_info("WorkflowEngine", f"Starting workflow execution: [{self.name}]")
        self.context["initial_input"] = initial_input
        current_value = initial_input

        for index, step in enumerate(self.steps, start=1):
            service_name = step["service"]
            log_info("WorkflowEngine", f"Executing step {index}/{len(self.steps)}: [{service_name}]")
            
            try:
                # Dynamically retrieve the tool from the service registry
                func = registry.get_service(service_name)
                
                # Determine what argument to feed the step
                if step["constant"] is not None:
                    arg = step["constant"]
                elif step["input_key"] is not None:
                    arg = self.context.get(step["input_key"])
                else:
                    arg = current_value

                # Run the service step
                result = func(arg)
                
                # Cache the outcome in our context database workspace
                if step["output_key"] is not None:
                    self.context[step["output_key"]] = result
                
                current_value = result
                
            except Exception as e:
                log_error("WorkflowEngine", f"Workflow [{self.name}] crashed at step {index} ({service_name}): {e}")
                raise RuntimeError(f"Workflow '{self.name}' failed at step {service_name}: {e}")

        log_info("WorkflowEngine", f"Workflow [{self.name}] completed successfully.")
        return current_value