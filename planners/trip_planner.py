import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

async def plan(data, destination, start_date, end_date, interests):
    """
    Generates a trip plan using the scraped data and user's interests.
    This is where you can leverage the power of GitHub Copilot to generate a personalized itinerary.
    """
    print("Generating trip plan...")

    # Prepare the prompt for the OpenAI API
    prompt = f"Create a trip plan for {destination} from {start_date} to {end_date}. \
              The user is interested in {', '.join(interests)}. \
              Here is some data scraped from travel websites: {data}"

    # In a real implementation, you would make a call to the OpenAI API.
    # For this example, we'll return a dummy plan.
    # response = openai.Completion.create(
    #     engine="text-davinci-003",
    #     prompt=prompt,
    #     max_tokens=1024
    # )
    # return response.choices[0].text.strip()

    return f"Trip plan for {destination} based on your interests: {', '.join(interests)}"
