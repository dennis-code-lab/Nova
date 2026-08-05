"""
Nova Engine v96
Application Entry Point & Interactive Router
"""

import os
import sys

from modules.decision_engine import DecisionEngine
from modules.engineering_command_router import EngineeringCommandRouter
from modules.engineering_controller import EngineeringController
from modules.engineering_planner import EngineeringPlanner
from modules.engineering_runtime import EngineeringRuntime


def handle_command(
    user_input: str,
    runtime: EngineeringRuntime,
    engineering_router: EngineeringCommandRouter,
    planner: EngineeringPlanner,
    controller: EngineeringController,
    adr: DecisionEngine,
):
    """
    Executes commands using the shared runtime, router, planner, controller, and decision engine instances.
    """
    cmd_lower = user_input.lower().strip()

    # Call the command router first
    result = engineering_router.execute(user_input)
    if result is not None:
        print(result)
        return

    if cmd_lower in ["help", "commands"]:
        print("\nAvailable Commands:")
        print("  plan                    - View roadmap dashboard")
        print("  engineering roadmap     - Generate autonomous engineering roadmap")
        print("  engineering progress    - Show engineering completion progress")
        print("  engineering milestones  - Show engineering milestone progress")
        print("  engineering achievements - View completed engineering milestones")
        print("  engineering sprint      - View active engineering sprint")
        print("  engineering forecast    - Forecast engineering health improvements")
        print("  engineering simulate <module> - Simulate the impact of refactoring a module")
        print("  engineering decision    - Generate Nova's top engineering recommendation")
        print("  engineering complete <module> - Mark an engineering module as completed")
        print("  sprints                 - View sprint progression")
        print("  next task               - Get active priority task")
        print("  estimate <id>           - View task estimation metrics")
        print("  why <id>                - View intelligent priority reasoning")
        print("  add task <title>        - Add new task to backlog")
        print("  complete task <id>      - Mark task completed")
        print("  decision list           - View architecture decisions")
        print("  decision show <id>      - Show specific ADR")
        print("  dependency analyze      - Analyze project dependencies")
        print("  analyze dependencies    - Alias for dependency analysis")
        print("  engineering impact      - Generate engineering impact report")
        print("  engineering overview    - Project-wide engineering dashboard")
        print("  engineering dashboard   - Executive Engineering Dashboard")
        print("  release notes           - Generate version release notes")
        print("  engineering explain <m>- Explain engineering score and risk")
        print("  engineering advise <m>  - Generate engineering improvement advice")
        print("  engineering report <m>  - View full engineering report for a module")
        print("  engineering plan <m>    - View refactor plan for a module")
        print("  engineering predict <m> - View affected dependency modules")
        print("  engineering risk <m>    - Evaluate risk score and reasons for a module")

    elif cmd_lower in ["plan", "roadmap"]:
        print(planner.format_plan_dashboard())

    elif cmd_lower == "engineering roadmap":
        print(runtime.roadmap())

    elif cmd_lower == "engineering progress":
        print(runtime.progress())

    elif cmd_lower == "engineering milestones":
        print(runtime.milestones())

    elif cmd_lower == "engineering achievements":
        print(runtime.achievements())

    elif cmd_lower == "engineering sprint":
        print(runtime.sprint())

    elif cmd_lower == "engineering forecast":
        print(runtime.forecast())

    elif cmd_lower.startswith("engineering simulate"):
        parts = user_input.split(maxsplit=2)
        if len(parts) < 3:
            print("Usage: engineering simulate <module>")
        else:
            print(runtime.simulate(parts[2]))

    elif cmd_lower == "engineering decision":
        print(runtime.decision())

    elif cmd_lower.startswith("engineering complete"):
        parts = user_input.split(maxsplit=2)
        if len(parts) < 3:
            print("Usage: engineering complete <module>")
        else:
            runtime.complete(parts[2])
            print(f"\nMarked '{parts[2]}' as completed.")

    elif cmd_lower in ["sprints"]:
        print(planner.format_sprint_roadmap())

    elif cmd_lower in ["next task", "next"]:
        task = planner.get_next_task()
        if task:
            print(f"\n[NEXT TASK] [{task['id']}] {task['title']}")
            print(
                f"Priority: {task['priority']} | "
                f"Effort: {task['effort']} | "
                f"Risk: {task['risk']}"
            )
        else:
            print("\nAll active roadmap tasks are marked complete!")

    elif cmd_lower.startswith("estimate"):
        task_id = user_input.split()[-1]
        print(planner.estimate_task(task_id))

    elif cmd_lower.startswith("why"):
        task_id = user_input.split()[-1]
        print(planner.get_intelligent_priority(task_id))

    elif cmd_lower.startswith("add task"):
        title = " ".join(user_input.split()[2:]).strip()
        if title:
            nt = planner.add_task(title)
            print(f"\n[OK] Task [{nt['id']}] '{nt['title']}' added to backlog.")
        else:
            print("\nPlease specify a task title.")

    elif cmd_lower.startswith("complete task"):
        task_id = user_input.split()[-1].upper()
        roadmap = planner.load_roadmap()
        found = False

        for t in roadmap.get("tasks", []):
            if t["id"] == task_id:
                t["status"] = "DONE"
                found = True
                break

        if found:
            planner.save_roadmap(roadmap)
            print(f"\n[OK] Task [{task_id}] completed.")

            create_adr = input(
                f"Create Architecture Decision Record for {task_id}? [y/N]: "
            ).strip().lower()

            if create_adr == "y":
                title = input("ADR Title: ").strip()
                decision = input("Decision: ").strip()
                reason = input("Reason: ").strip()
                tradeoffs = input("Tradeoffs: ").strip()

                new_adr = adr.create_decision(
                    title,
                    decision,
                    reason,
                    tradeoffs,
                )
                print(f"[OK] Logged {new_adr['id']}")
        else:
            print(f"\nTask {task_id} not found.")

    elif cmd_lower == "decision list":
        print(adr.format_list())

    elif cmd_lower.startswith("decision show"):
        adr_id = user_input.split()[-1]
        print(adr.format_adr(adr_id))

    elif cmd_lower in [
        "dependency analyze",
        "analyze dependencies",
        "engineering impact",
    ]:
        print(controller.analyze_dependencies())

    elif cmd_lower == "release notes":
        print(controller.generate_release_notes())

    elif cmd_lower == "engineering overview":
        print(runtime.overview())

    elif cmd_lower == "engineering dashboard":
        print(runtime.dashboard())

    elif cmd_lower.startswith("engineering explain "):
        module = user_input.split(maxsplit=2)[2]
        print(runtime.explain(module))

    elif cmd_lower.startswith("engineering advise "):
        module = user_input.split(maxsplit=2)[2]
        print(runtime.advise(module))

    elif cmd_lower.startswith("engineering report "):
        module = user_input[len("engineering report "):].strip()
        print(runtime.report(module))

    elif cmd_lower.startswith("engineering plan "):
        module = user_input[len("engineering plan "):].strip()
        print(runtime.plan(module))

    elif cmd_lower.startswith("engineering predict "):
        module = user_input[len("engineering predict "):].strip()
        result = runtime.predict(module)

        if not result["found"]:
            print(f"\nModule '{module}' was not found.")
        else:
            print(f"\nModule: {module}")
            print(f"Affected Modules ({result['affected_count']}):")
            if result["affected_modules"]:
                for m in result["affected_modules"]:
                    print(f"  • {m}")
            else:
                print("  None")

    elif cmd_lower.startswith("engineering risk "):
        module = user_input[len("engineering risk "):].strip()
        risk = runtime.risk(module)

        print(f"\nModule: {risk.module}")
        print(f"Risk: {risk.risk}")
        print(f"Engineering Score: {risk.engineering_score}")
        print(f"Dependencies: {risk.dependency_count}")
        print("\nReasons:")
        for reason in risk.reasons:
            print(f"  • {reason}")

    else:
        print(
            f"\nNova Technical Lead: Understood context regarding "
            f"'{user_input}'. Standing by for execution instructions."
        )


def interactive_mode(
    engineering: EngineeringRuntime,
    engineering_router: EngineeringCommandRouter,
    planner: EngineeringPlanner,
    controller: EngineeringController,
    adr: DecisionEngine,
):
    print("==================================================")
    print("      NOVA ENGINE v96 - AUTONOMOUS TECH LEAD      ")
    print("      Interactive Assistant Shell Active          ")
    print("      Type 'help' for commands, 'exit' to quit.   ")
    print("==================================================\n")

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nBooting down Nova Engine. Goodbye!")
                break

            if not user_input:
                continue

            handle_command(
                user_input,
                engineering,
                engineering_router,
                planner,
                controller,
                adr,
            )

        except (KeyboardInterrupt, EOFError):
            print("\nExiting session.")
            break


def cli_mode(
    args: list,
    engineering: EngineeringRuntime,
    engineering_router: EngineeringCommandRouter,
    planner: EngineeringPlanner,
    controller: EngineeringController,
    adr: DecisionEngine,
):
    command = " ".join(args).strip()
    handle_command(
        command,
        engineering,
        engineering_router,
        planner,
        controller,
        adr,
    )


if __name__ == "__main__":
    # Create single runtime instance at entry point
    engineering = EngineeringRuntime()
    engineering_router = EngineeringCommandRouter(engineering)
    planner = EngineeringPlanner()
    controller = EngineeringController()
    adr = DecisionEngine()

    if len(sys.argv) == 1:
        interactive_mode(
            engineering,
            engineering_router,
            planner,
            controller,
            adr,
        )
    else:
        cli_mode(
            sys.argv[1:],
            engineering,
            engineering_router,
            planner,
            controller,
            adr,
        )