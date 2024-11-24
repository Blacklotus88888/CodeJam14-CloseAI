import os
from openai import OpenAI
import pandas as pd
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime

class CarSalesAssistant:
    """
    Main class for handling car sales conversations using LLM.
    Focuses solely on sales interaction without appointment management.
    """
    
    def __init__(self, model: str = "gpt-4"):
        """
        Initialize the car sales assistant
        
        Args:
            model (str): OpenAI model name to use. Defaults to "gpt-4"
        """
        self.client = OpenAI()  # API key from environment variables
        self.model = model
        self.conversation_history = []
        self.car_data = None
        
    def load_car_data(self, csv_path: str) -> None:
        """
        Load car inventory data from CSV file
        
        Args:
            csv_path (str): Path to the CSV file containing car data
        """
        try:
            self.car_data = pd.read_csv(csv_path)
            car_info = self.car_data.to_string(index=False)
            self.car_info = f"Available car data:\n{car_info}"
        except Exception as e:
            print(f"Error loading CSV file: {str(e)}")
            self.car_info = "No car data available"
    
    def create_system_prompt(self) -> str:
        """
        Create the system prompt for the LLM
        
        Returns:
            str: Complete system prompt including car data
        """
        base_prompt = """You are Hengyi, an experienced car salesperson who is professional, adaptive, and focused on closing deals. Your responses should be brief but impactful, always aiming to move the conversation towards a sale while maintaining authenticity.

[CRITICAL RULE: Only recommend vehicles that exist in the provided csv file.]

Core Behaviors:

1. Response Style
- Keep all responses under 3 sentences unless specifically asked for details
- Lead with the most relevant information first
- Use natural, conversational language
- Maintain professionalism even when faced with casual or rude behavior

2. Sales Strategy
- Always include price ranges when mentioning specific models
- Respond to budget-related keywords (like "broke", "expensive", "cheap") with appropriate options
- When lacking inventory information, focus on general recommendations and invite store visits
- Look for opportunities to suggest viewing available vehicles in person

3. Customer Interaction
- Match the customer's communication style while staying professional
- Handle non-serious queries (like jokes) with brief, friendly responses before steering back to sales
- For unclear requests, provide one quick clarification question followed by a suggestion
- When faced with rudeness, respond once professionally then wait for serious queries

4. Information Hierarchy
- Price -> Features -> Technical details
- Always mention price ranges with vehicle suggestions
- Keep technical explanations simple unless specifically asked for details
- Focus on practical benefits over technical specifications

5. Closing Techniques
- End each response with a subtle call to action
- Suggest store visits or test drives when interest is shown
- Provide clear next steps for interested customers
- Be direct about availability and options

Response Templates:
- For jokes/non-serious queries: Brief acknowledgment + one vehicle suggestion
- For rude comments: Make a joke and then steer the conversation to sales
- For specific vehicle interests: Price range + key features + next step
- For general queries: 2-3 options with price ranges + simple comparison

When suggesting vehicles, use this format:
Brand Model Name Price Range Key Benefit Available Action
"""
        return base_prompt + (self.car_info if hasattr(self, 'car_info') else "No car data available")
    
    def get_completion(self, user_query: str) -> str:
        """
        Get response from OpenAI API
        
        Args:
            user_query (str): User's input message
            
        Returns:
            str: Assistant's response
        """
        messages = [
            {
                "role": "system", 
                "content": self.create_system_prompt()
            }
        ]
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add user's new question
        messages.append({"role": "user", "content": user_query})
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            
            response = completion.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_query})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
            
        except Exception as e:
            return f"Sorry, an error occurred: {str(e)}"
    
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []


class AppointmentManager:
    """
    Handles the detection of test drive intent and manages appointment bookings.
    Separate from the main conversation flow.
    """
    
    def __init__(self):
        """Initialize the appointment manager"""
        self.appointments_dir = "appointments"
        
        # Create appointments directory if not exists
        if not os.path.exists(self.appointments_dir):
            os.makedirs(self.appointments_dir)
    
    def detect_test_drive_intent(self, salesman_response: str, user_response: str) -> bool:
        """
        Detect if there's a test drive suggestion and positive user response
        
        Args:
            salesman_response (str): The salesman's last response
            user_response (str): The user's response
            
        Returns:
            bool: True if test drive intent is detected
        """
        # Test drive related keywords in salesman's response
        test_drive_keywords = [
            "test drive", "test-drive", "come see", 
            "visit us", "schedule a visit", "book an appointment",
            "come by", "check it out", "see it in person"
        ]
        
        # Positive response keywords from user
        positive_responses = [
            "yes", "sure", "okay", "ok", "definitely", 
            "absolutely", "would love to", "let's do it",
            "sounds good", "great", "perfect"
        ]
        
        # Check if salesman suggested test drive
        has_test_drive = any(keyword in salesman_response.lower() 
                           for keyword in test_drive_keywords)
                           
        # Check if user responded positively
        is_positive = any(response in user_response.lower() 
                         for response in positive_responses)
                         
        return has_test_drive and is_positive
    
    def create_appointment_form(self) -> Dict:
        """
        Create a new appointment form template
        
        Returns:
            Dict: Empty appointment form structure
        """
        return {
            "name": None,
            "contact": None,
            "preferred_time": None,
            "vehicle": None,
            "notes": None
        }
    
    def save_appointment(self, appointment_data: Dict) -> None:
        """
        Save appointment to JSON file
        
        Args:
            appointment_data (Dict): Collected appointment information
        """
        try:
            # Add metadata
            appointment_data.update({
                "appointment_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            })
            
            # Generate filename
            filename = os.path.join(
                self.appointments_dir, 
                f"appointment_{appointment_data['appointment_id']}.json"
            )
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(appointment_data, f, indent=4)
                
            print(f"Appointment saved: {filename}")
            
        except Exception as e:
            print(f"Error saving appointment: {str(e)}")


def main():
    """Main function to run the car sales assistant"""
    
    # Ensure API key is set
    api_key = "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"
    os.environ['OPENAI_API_KEY'] = api_key
    
    # Initialize components
    assistant = CarSalesAssistant()
    appointment_manager = AppointmentManager()
    
    # Load car data
    csv_path = r"/Users/dudukoo/Downloads/CodeJam14-CloseAI-main/src/modelTrain/cars.csv"
    assistant.load_car_data(csv_path)
    
    print("\nCar Sales Assistant is ready!")
    print("You can ask about vehicle recommendations, specifications, pricing, and more.")
    print("Type 'exit' to end the conversation.")
    
    last_response = ""  # Store last response for intent detection
    
    # Start conversation loop
    while True:
        # Get user input
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("\nThank you for your time. Goodbye!")
            break
        
        # Get salesman response
        response = assistant.get_completion(user_input)
        print(f"\nHengyi: {response}")
        
        # Check for test drive intent
        if appointment_manager.detect_test_drive_intent(last_response, user_input):
            print("\nLet's schedule your test drive!")
            
            # Create appointment form
            appointment = appointment_manager.create_appointment_form()
            
            # Collect information
            print("\nPlease provide the following information:")
            appointment["name"] = input("Your name: ")
            appointment["contact"] = input("Contact number: ")
            appointment["preferred_time"] = input("Preferred time: ")
            appointment["vehicle"] = input("Vehicle of interest: ")
            appointment["notes"] = input("Any additional notes (optional): ")
            
            # Save appointment
            appointment_manager.save_appointment(appointment)
            
            print("\nThank you! Your appointment has been scheduled.")
        
        # Update last response
        last_response = response


if __name__ == "__main__":
    main()