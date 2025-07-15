import asyncio
from scrapers import ctrip_scraper, hsr_scraper, dianping_scraper
from planners import trip_planner

async def main():
    """
    Main function to run the trip planning process.
    """
    # Get user input for destination, start_date, end_date, and interests
    destination = input("Enter your destination: ")
    start_date = input("Enter the start date (YYYY-MM-DD): ")
    end_date = input("Enter the end date (YYYY-MM-DD): ")
    interests = input("Enter your interests (comma-separated): ").split(',')

    # Scrape data from different sources
    ctrip_data = await ctrip_scraper.scrape(destination)
    hsr_data = await hsr_scraper.scrape(destination)
    dianping_data = await dianping_scraper.scrape(destination)

    # Combine and process the scraped data
    all_data = {
        "ctrip": ctrip_data,
        "hsr": hsr_data,
        "dianping": dianping_data,
    }

    # Generate the trip plan
    trip_plan = await trip_planner.plan(all_data, destination, start_date, end_date, interests)

    # Print the trip plan
    print(trip_plan)

if __name__ == "__main__":
    asyncio.run(main())
