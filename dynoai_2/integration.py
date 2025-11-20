import os
import sys
import asyncio
from dotenv import load_dotenv

# Import DeepCode components
# Note: ensure deepcode-hku is installed or DeepCode root is in PYTHONPATH
try:
    from cli.cli_app import CLIApp
    from workflows.agent_orchestration_engine import execute_chat_based_planning_pipeline
except ImportError:
    print("DeepCode not found. Please install deepcode-hku or add it to PYTHONPATH.")
    sys.exit(1)

# Load environment variables
load_dotenv()

class DeepCodeIntegrator:
    """
    Integrates DeepCode capabilities into DynoAI_2.
    """
    def __init__(self):
        self.app = CLIApp()
        
    async def generate_feature(self, requirement: str):
        """
        Uses DeepCode to generate a feature based on requirements.
        """
        print(f"Generating feature for: {requirement}")
        
        # Initialize the MCP app (DeepCode agent)
        init_result = await self.app.initialize_mcp_app()
        if init_result["status"] != "success":
            raise Exception(f"Failed to initialize DeepCode: {init_result['message']}")
            
        try:
            # Use the chat-based pipeline to generate code
            # This will create a new project in deepcode_lab/papers/chat_project_...
            # In a real integration, we might want to direct this output to a specific folder
            
            def simple_progress(percent, message):
                print(f"[Progress {percent}%] {message}")
                
            result = await execute_chat_based_planning_pipeline(
                user_input=requirement,
                logger=self.app.logger,
                progress_callback=simple_progress
            )
            return result
        finally:
            await self.app.cleanup_mcp_app()

async def main():
    integrator = DeepCodeIntegrator()
    
    print("DynoAI_2 - DeepCode Integration Demo")
    print("------------------------------------")
    
    # Example usage: Ask DeepCode to generate a login module
    try:
        result = await integrator.generate_feature("Create a secure login module with Flask and JWT")
        print("\nGeneration Result:")
        print(result)
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())

