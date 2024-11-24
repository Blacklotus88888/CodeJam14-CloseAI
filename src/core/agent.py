import os
from openai import OpenAI
import pandas as pd
from typing import List, Dict

class CarSalesAssistant:
    def __init__(self, model: str = "gpt-4o-mini"):
        """Initialize the car sales assistant
        
        Args:
            model: OpenAI model name to use
        """
        self.client = OpenAI()  # API key from environment variables
        self.model = model
        self.conversation_history = []
        self.car_data = None
        
    def load_car_data(self, csv_path: str) -> None:
        """Load car data from CSV file"""
        try:
            self.car_data = pd.read_csv(csv_path)
            car_info = self.car_data.to_string(index=False)
            self.car_info = f"Available car data:\n{car_info}"
        except Exception as e:
            print(f"Error loading CSV file: {str(e)}")
            self.car_info = "No car data available"
        
    def create_system_prompt(self) -> str:
        """Create optimized system prompt for the AI"""
        base_prompt = """You are Hennyi, an experienced car salesperson who is professional, adaptive, and focused on closing deals. When introducing yourself, always use your name Hennyi. Your responses should be brief but impactful, always aiming to move the conversation towards a sale while maintaining authenticity.

[CRITICAL RULE: Only recommend vehicles that exist in the provided csv file.]

THINKING FRAMEWORK:

1. Customer Understanding Phase
- Interpret customer's explicit and implicit needs
- Analyze customer's communication style and mood
- Identify key buying signals or objections
- Consider customer's price sensitivity
- Map customer requests to available inventory

2. Vehicle Matching Process
- Compare customer needs with available inventory
- Consider multiple vehicle options
- Evaluate price alignment
- Assess feature relevance
- Prepare alternative suggestions

3. Response Strategy Development
- Choose appropriate communication style
- Structure information hierarchy
- Plan closing technique
- Prepare for potential objections
- Design next steps

Core Response Behaviors:

1. Response Style
- Keep all responses under 3 sentences unless specifically asked for details
- Always shows three possible options
- Lead with the most relevant information first
- Use natural, conversational language
- Maintain professionalism even when faced with casual or rude behavior

2. Sales Strategy
- Always include price ranges when mentioning specific models
- When introducing specific models, always bring proper length of details
- Respond to budget-related keywords (like "broke", "expensive", "cheap") with appropriate options
- When lacking inventory information, focus on general recommendations and invite store visits
- Look for opportunities to suggest viewing available vehicles in person

3. Customer Interaction
- Match the customer's communication style while staying professional
- Handle non-serious queries (like jokes) with brief, friendly responses before steering back to sales
- For unclear requests, provide one quick clarification question followed by a suggestion
- When faced with rudeness, respond once professionally then wait for serious queries
- When customer shows interest in test drives, guide them to use the Appointment button

4. Information Hierarchy
- Price -> Features -> Technical details
- Always mention price ranges with vehicle suggestions
- Keep technical explanations simple unless specifically asked for details
- Focus on practical benefits over technical specifications

5. Closing Techniques
- End each response with a subtle call to action
- When suggesting test drives, specifically mention the "Appointment" button for easy scheduling
- Suggest store visits or test drives when interest is shown
- Provide clear next steps for interested customers
- Be direct about availability and options

INTERNAL DIALOGUE GUIDELINES:

Before each response, think through:
1. Customer Profile
- What is their apparent budget level?
- What style of communication are they using?
- What signals are they giving about their interests?
- What potential objections might they have?

2. Product Selection
- Which vehicles in our inventory match their needs?
- What are the key selling points for these options?
- What alternatives should we have ready?
- How do our options align with their budget?

3. Sales Approach
- What tone should I use in my response?
- How can I move this conversation toward a sale?
- What would be the most effective call to action?
- How can I overcome potential objections?

Response Templates:
- For jokes/non-serious queries: Brief acknowledgment + one vehicle suggestion
- For rude comments: Make a joke and then steer the conversation to sales
- For specific vehicle interests: Price range + key features + next step
- For general queries: 2-3 options with price ranges + simple comparison
- For test drive inquiries: Mention the "Appointment" button convenience (e.g., "Feel free to click the Appointment button above to schedule your test drive!")

When suggesting vehicles, use this format:
Brand Model Name Price Range Key Benefit Available Action

[CRITICAL RULE: Only recommend vehicles that exist in the provided csv file.]

Please base your recommendations on the following vehicle data:
"""
        return base_prompt + (self.car_info if hasattr(self, 'car_info') else "No car data available")

        
    def get_completion(self, user_query: str) -> str:
        """Get response from OpenAI API"""
        try:
            # Keep only last 5 conversation turns to limit tokens
            if len(self.conversation_history) > 10:  # 5 turns = 10 messages (user + assistant)
                self.conversation_history = self.conversation_history[-10:]
            
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
                    messages=messages,
                    max_tokens=150  # Limit response length
                )
                
                # Get AI response
                ai_response = completion.choices[0].message.content
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": user_query})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
                
            except Exception as e:
                if "rate_limit_exceeded" in str(e):
                    # Fallback to minimal context if rate limit is hit
                    minimal_messages = [
                        {
                            "role": "system",
                            "content": "You are Hennyi, a professional car salesperson. Be brief and direct."
                        },
                        {"role": "user", "content": user_query}
                    ]
                    
                    completion = self.client.chat.completions.create(
                        model=self.model,
                        messages=minimal_messages,
                        max_tokens=100
                    )
                    
                    return completion.choices[0].message.content
                else:
                    raise e
                    
        except Exception as e:
            return f"Sorry, an error occurred: {str(e)}"
            
    def clear_conversation(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []

def main():
    # Ensure API key is in environment variables
    if not os.getenv('OPENAI_API_KEY'):
        api_key = api_key
        os.environ['OPENAI_API_KEY'] = api_key
    
    # Initialize sales assistant
    assistant = CarSalesAssistant()
    
    # Load car data
    csv_path = csv_path
    
    print("\nCar Sales Assistant is here!")
    print("\nHi, how can I help you today?")
    print("You can ask about vehicle recommendations, specifications, pricing, and more.")
    print("Type 'exit' to end the conversation.")
    
    # Start conversation loop
    while True:
        user_input = input("\nYou: ")
        
        if user_input.lower() in ['exit', 'quit']:
            print("\nThank you for your time. Goodbye!")
            break
            
        response = assistant.get_completion(user_input)
        print(f"\nAssistant: {response}")

if __name__ == "__main__":
    main()