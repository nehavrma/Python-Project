import sqlite3 as sql
import sql_tools  
# COPYRIGHT Brian Harrington, 2022
# slightly modified print_select function to help in vacation_planner function
import csv
import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

#Travel Buddy helps users find their ideal travel destinations based on their weather preferences, budget, and safety data

user_credentials_list = []

# user creates username and password
# then logs in


def login_or_create():
  print("Welcome to Travel Buddy!")  # this is a good name hahaa
  # ask user if they want to log in or create an account
  choice = 'X'
  while (choice != '3'):
    choice = input("""
    Would you like to:
    1. Create an account
    2. Log in
    3. Exit

    Choose your option: """)
    # if the user wants to create their account
    if choice == '1':
      #call create account function
      new_user = create_account()
      user_credentials_list.append(new_user)
      print("New user details: ", new_user)

    # if the user wants to log in to account
    elif choice == '2':
      #call login function
      logged_in_user = login()
      if logged_in_user:
        #if user successfully logs in, present vacation planner
        continue_planning = True
        while continue_planning == True:
           continue_planning = vacation_planner()

    # if the user wants to exit
    elif choice == '3':
      print("Goodbye!")
      break

    else:
      print("Invalid choice. Please try again.")

def create_account():
  # dictionary for storing user information
  user_credentials = {}
  # ask user for username and password
  username = input("Enter your new username: ")
  password = input("Enter your new password: ")
  # store username and password in dictionary
  user_credentials['username'] = username
  user_credentials['password'] = password
  # confirm account was created
  print("Account created successfully!")
  return user_credentials


def login():
  # ask user for username and password
  entered_username = input("Enter your username: ")
  entered_password = input("Enter your password: ")
  # check if username and password match stored user credentials
  for user in user_credentials_list:
    if user['username'] == entered_username and user[
        'password'] == entered_password:
      print("Login successful!")
      return user
  print(
      "Login unsuccessful. Please check your username and password and try again. "
  )


# the vacation planner tool (ONLY presented to logged in users)
month_input = ""


def vacation_planner():
  print("\n\n")
  print("Welcome to Travel Buddy!")
  print("1. View all our destinations")
  print("2. Let us help you choose your destination!")
  print("0: Log out")
  # print("3. Choose your activities")
  # print("4. Enter your budget")
  choice = input("What would you like to do?: ")
  db_handle = sql.connect("final_project.db")

  if choice == 1 or choice == 2:
    csv_file = open('city_temperature_new.csv', 'r')
    # data downloaded from https://www.kaggle.com/datasets/sudalairajkumar/daily-temperature-of-major-cities 
    # stored in city_temperature_new.csv

    # convert csv to table to manipulate data with query
    sql_tools.csv_to_table(db_handle, csv_file, 'Temp', ['TEXT', 'TEXT', 'TEXT', 'REAL', 'REAL', 'REAL', 'REAL'])
    csv_file.close()
    with open("temp_output_all.csv", "w", newline="") as file_handle:
        # take avg of temp for each month
        # display by City
        sql_query = """
        SELECT Region, Country, City, Month, AVG(AvgTemperature) AS AvgTempPerMonth
        FROM Temp
        GROUP BY Month, City
        ORDER BY City ASC
        """
        sql_tools.select_to_csv(db_handle, file_handle, sql_query)
        csv_file = open('temp_output_all.csv', 'r')

        #save query results as csv for further use in filtering by weather and month
        sql_tools.csv_to_table(db_handle, csv_file, 'OutputAll', ['TEXT', 'TEXT', 'TEXT', 'REAL', 'REAL'])
        csv_file.close()

  if choice == "1":
    # show all cities in the database 
    # calculate avg temp per year for each city
    sql_query = """
    SELECT Region, Country, City, AVG(AvgTempPerMonth) AS AvgTempAcrossYearPerCity
    FROM OutputAll
    GROUP BY City
    ORDER BY Region ASC
    """
    # print to terminal
    sql_tools.print_select(db_handle, sql_query)
    return True

  elif choice == "2":
    # let user choose city and month
    print("""
          
    Thank you for letting us help you choose your destination! 
    We're going to ask you a few questions to help us narrow down your search.
          
          """
          )
    month_input = int(input("Which month are you travelling in (eg. enter 12 for Dec): "))

    # month_input cannot be greater than 12
    if ((month_input > 12) or (month_input < 1)):
      return None

    else:
      weather = "X"
      while weather != "E":
            weather = str(
                input("""What kind of weather do you want:
            1. Cold: 55ºF and below
            2. Cool: 56ºF to 65ºF
            3. Mild: 66ºF to 75ºF
            4. Warm: 75ºF to 85ºF
            5. Hot: Above 85ºF

            Type "E" to exit

            Please choose from these options (1-5): """))
            # definitions from https://www.sun-sentinel.com/2014/10/17/what-exactly-does-hot-and-cold-mean-anyhow/#:~:text=Cold%3A%20Below%2050%20degrees,Hot%3A%20Above%2090
            # initialised has_records as false in case of weather input not having any output
            has_records = False

            if weather == "1":
                # define temp range and use month variable from month_input
                sql_query = """
                SELECT Region, Country, City, Month, AvgTempPerMonth
                FROM OutputAll
                WHERE 
                    Month = '{0}' AND AvgTempPerMonth < 55
                GROUP BY City
                ORDER BY AvgTempPerMonth ASC
                """
                # print results
                sql_query = sql_query.format(month_input)
                has_records = sql_tools.print_select(db_handle, sql_query)

            elif weather == "2":
                # define temp range and use month variable from month_input (repeat from step 1)
                sql_query = """
                SELECT Region, Country, City, Month, AvgTempPerMonth
                FROM OutputAll
                WHERE 
                    Month = '{0}' AND AvgTempPerMonth BETWEEN 56 AND 65
                GROUP BY City
                ORDER BY AvgTempPerMonth ASC
                """
                # print results
                sql_query = sql_query.format(month_input)
                has_records = sql_tools.print_select(db_handle, sql_query)

            elif weather == "3":
                # define temp range and use month variable from month_input (repeat from step 1)
                sql_query = """
                SELECT Region, Country, City, Month, AvgTempPerMonth
                FROM OutputAll
                WHERE 
                    Month = '{0}' AND AvgTempPerMonth BETWEEN 66 AND 75
                GROUP BY City
                ORDER BY AvgTempPerMonth ASC
                """
                # print results
                sql_query = sql_query.format(month_input)
                has_records = sql_tools.print_select(db_handle, sql_query)

            elif weather == "4":
                # define temp range and use month variable from month_input (repeat from step 1)
                sql_query = """
                SELECT Region, Country, City, Month, AvgTempPerMonth
                FROM OutputAll
                WHERE 
                    Month = '{0}' AND AvgTempPerMonth BETWEEN 75 AND 85
                GROUP BY City
                ORDER BY AvgTempPerMonth ASC
                """
                # print results
                sql_query = sql_query.format(month_input)
                has_records = sql_tools.print_select(db_handle, sql_query)

            elif weather == "5":
                # define temp range and use month variable from month_input (repeat from step 1)
                sql_query = """
                SELECT Region, Country, City, Month, AvgTempPerMonth
                FROM OutputAll
                WHERE 
                    Month = '{0}' AND AvgTempPerMonth > 85
                GROUP BY City
                ORDER BY AvgTempPerMonth ASC
                """
                # print results
                sql_query = sql_query.format(month_input)
                has_records = sql_tools.print_select(db_handle, sql_query)

            else:
                # else: exit loop
                print("Invalid input")
                break

            if has_records:
                # ask input for city name to show user current weather
                city_name = str(input("\n\nChoose one of these cities to view current weather: "))

                # importing geopy library and Nominatim class
                # START code from documentation found here: https://geopy.readthedocs.io/en/stable/#installation

                from geopy.geocoders import Nominatim
                # calling the Nominatim tool and create Nominatim class
                loc = Nominatim(user_agent="Geopy Library")
                # END code from documentation

                # entering the location name
                getLoc = loc.geocode(city_name)

                # getting the latitude and longitude
                lat = getLoc.latitude
                lon = getLoc.longitude

                # START code modified from ChatGPT's answer for the prompt
                # "how to use api keys in python code"
                # got the api from openweather
                api_key = '0b99971e6da1b217a9810df1afea5bef'
                url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}'
                # Make the API request
                response = requests.get(url)

                # Check if the request was successful (status code 200)
                if response.status_code == 200:
                    weather_data = response.json()
                    # Process the weather data as needed
                    print(weather_data)

                else:
                    print(f"Failed to fetch data. Status code: {response.status_code}")
                    break
                    # END code modified from ChatGPT's answer for the prompt "how to use api keys in python"

                visual = str(input("\nDo you want to view visuals for this data? Enter 'yes' or 'no': "))
              # the visual is an interactive graph that shows average temperature for the chosen city over the 12 months

                if visual != "no":
                  # start of code modified from 
                  #https://matplotlib.org/stable/gallery/images_contours_and_fields/colormap_interactive_adjustment.html#interactive-adjustment-of-colormap-range
                    # https://www.geeksforgeeks.org/how-to-draw-2d-heatmap-using-matplotlib-in-python/
                    # https://stackoverflow.com/questions/69968235/pivot-table-in-proper-order-for-the-heatmap
                    # https://www.upgrad.com/blog/heatmap-in-python/
                    # GPT and Bing at points in the code to understand or correct terms

                    # reading data from the initial CSV file
                    data = pd.read_csv('city_temperature_new.csv')

                    # bypassing city_name case sensitivity
                    city_name = city_name.capitalize() #karachi to Karachi

                    # filtering data for a single city using city_name variable
                    city_data = data[data['City'] == city_name] # city name from earlier defined variable

                    # gandling NaN values by replacing them with the mean of non-NaN values
                    city_data['AvgTemperature'] = city_data['AvgTemperature'].fillna(city_data['AvgTemperature'].mean())
                    # this is to bypass error messages regarding NaN values

                    # pivoting the data to create a heatmap for the selected city
                    pivot_data = city_data.pivot_table(index='Year', columns='Month', values='AvgTemperature', aggfunc='mean')

                    # checking if pivot_data contains valid values
                    if pivot_data.isnull().values.any():
                        print("NaN values present in pivot_data. Please handle NaN values in the dataset.")

                    # plotting the heatmap with colormap adjustment
                    data2d = pivot_data.to_numpy()

                    fig, ax = plt.subplots()
                    im = ax.imshow(data2d, cmap='hot', interpolation='nearest')
                    ax.set_title(f'Interactive Heatmap for {city_name}')
                    ax.set_ylabel('Years') # adding the label for the y-axis representing years
                    ax.set_xlabel('Months') # adding the label for the x-axis representing months

                    # creating the axis for colorbar and sliders
                    axcolor = 'lightgoldenrodyellow'
                    ax_min = plt.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
                    ax_max = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)

                    # defining  initial values for colormap range
                    vmin_init = np.nanmin(data2d) if not np.isnan(np.nanmin(data2d)) else 0
                    vmax_init = np.nanmax(data2d) if not np.isnan(np.nanmax(data2d)) else 1

                    # creating sliders for colormap range adjustment
                    s_vmin = Slider(ax_min, 'Min', vmin_init, vmax_init, valinit=vmin_init)
                    s_vmax = Slider(ax_max, 'Max', vmin_init, vmax_init, valinit=vmax_init)

                    # updating the color mapping based on slider values
                    def update(val):
                        vmin = s_vmin.val
                        vmax = s_vmax.val
                        im.set_clim(vmin=vmin, vmax=vmax)
                        fig.canvas.draw_idle()

                    s_vmin.on_changed(update)
                    s_vmax.on_changed(update)

                    fig.colorbar(im, ax=ax, label='Average Temperature')

                    plt.show(block=False) # from https://github.com/matplotlib/matplotlib/issues/12692/ to continue after the graph
                    input() # to rectify the Github issue (https://github.com/matplotlib/matplotlib/issues/27389)
                    #need to PRESS ENTER TO CONTINUE
                    # break
                    # end of modified code

              
                # once the user has viewed the weather info and selected their city
                # they now have the option to get budget information on their
                # selected city
                #cost of living data dowloaded from: https://www.numbeo.com/cost-of-living/rankings_by_country.jsp
                cost_of_living_data = "cost_of_living.csv" 
                #hotel and restaurant data downloaded from: https://www.theglobaleconomy.com/rankings/hotel_and_restaurant_prices_wb/
                hotel_restaurant_data = "hotel_restaurant_prices.csv"
                temperature_data = "city_temperature_new.csv"
                get_budget_info(city_name, cost_of_living_data, hotel_restaurant_data, temperature_data)

                #once the user has viwewed the weather and budget info for their
                #selected city, they now have the option to get safety info
                #this function provides safety info for the country of the selected city
                #peace index data downloaded from: https://worldpopulationreview.com/country-rankings/safest-countries-in-the-world
                peace_index_data = 'peace_index_data.csv'
                get_safety_info(city_name, peace_index_data, temperature_data)
                visualize_gpi(city_name, peace_index_data, temperature_data)
                break
            else:
               print("\n\nNo cities found for the selected criteria! Please try again.\n\n")

    return True

  elif choice == "0":
    return False

  else:
    print("Invalid choice. Please try again.")
    return True


# this function provides budget info for the selected city
def get_budget_info(city, cost_of_living_data, hotel_restaurant_data, temperature_data):
    country = get_country_for_city(city, temperature_data)

    if country:
        print(f"\nWould you like travel budget information for {country}?")
        user_choice = input("Enter 'yes' or 'no': ").lower()

        # menu for budget information options
        if user_choice != 'no':
            print("\nChoose an option:")
            print("1. Cost of Living Information")
            print("2. Hotel and Restaurant Prices")
            option = input("Enter the option number (1 or 2): ")

            # option 1 - budget information based on cost of living
            if option == '1':
                get_cost_of_living_info(country, cost_of_living_data)

            # option 2 - budget information based on hotel + restaurant prices
            elif option == '2':
                get_hotel_restaurant_info(country, hotel_restaurant_data)

            # user did not select options 1 or 2 
            else:
                print("Invalid option. Please enter '1' or '2'.")

            #ask user if they want to visualize their data
            visualize_data = input("\nDo you want to visualize your data? Enter 'yes' or 'no': ")
            if visualize_data != 'no':
                if option == '1':
                  visualize_cost_of_living(country, cost_of_living_data)
                elif option == '2':
                  visualize_hotel_restaurant(country, hotel_restaurant_data)

            else:
              print("No worries! Let's move along to the next step. ")

        # user did not want budget information for their selected city
        # else:
        #     print("Thank you. Have a great day!")

    # if the chosen city is not in the temperature data
    else:
        print("City not found. Please try again.")

# this function retrieves the country that the selected city is in
def get_country_for_city(city_name, temperature_data):
    with open(temperature_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row

        for row in reader:
            if row[2].lower() == city_name.lower():
                return row[1]

# this function prints the cost of living info for the selected country,
# and also provides the rank of the country based on the cost of living info
def get_cost_of_living_info(country, cost_of_living_data):
    with open(cost_of_living_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        for row in reader:
            if row[1].lower() == country.lower():
                print(f"\nCost of Living Information for {country}:")
                print(f"Rank: {row[0]}")
                print(f"Cost of Living Index: {row[2]}")
                print(f"(note: cost of living index is based on the average cost of living in {country})")
                break
        else:
            print("Cost of Living information not found for the selected country.")

# this function prints the hotel and restaurant info for the selected country,
# and also prints the rank of the country based on the hotel and restaurant info
def get_hotel_restaurant_info(country, hotel_restaurant_data):
    with open(hotel_restaurant_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        for row in reader:
            if row[0].lower() == country.lower():
                print(f"\nHotel and Restaurant Price Index for {country}:")
                print(f"Global Rank: {row[2]}")
                print(f"Hotel and Restaurant Price Index: {row[1]}")
                print(f"(note: hotel and restaurant price index is based on the average hotel and restaurant prices in {country}, where a score of 100 is equivalent to the global average)")
                break
        else:
            print("Hotel and Restaurant Price Index information not found for the selected country.")

# this function visualizes the cost of living info for the selected country
def visualize_cost_of_living(country, cost_of_living_data):
  countries = []
  cost_of_living_index = []

  with open(cost_of_living_data, 'r') as file:
      reader = csv.reader(file)
      next(reader)  # skip header row
      for row in reader:
          countries.append(row[1])
          cost_of_living_index.append(float(row[2]))

  visualize_bar_graph(country, countries, cost_of_living_index, "Cost of Living Index")


# this function visualizes the hotel and restaurant info for the selected country
def visualize_hotel_restaurant(country, hotel_restaurant_data):
    countries = []
    hotel_restaurant_prices = []

    with open(hotel_restaurant_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        for row in reader:
            countries.append(row[0])
            hotel_restaurant_prices.append(float(row[1]))

    visualize_bar_graph(country, countries, hotel_restaurant_prices, "Hotel and Restaurant Prices")


# this function visualizes the bar graph for the selected country
def visualize_bar_graph(country, countries, values, title):
    x = np.arange(len(countries))
    width = 0.35

    fig, ax = plt.subplots()
    ax.bar(x, values, width, label=country, color='orange')
    ax.bar(x + width, values, width, label='Other Countries', color='blue')

    ax.set_xlabel('Countries')
    ax.set_ylabel(title)
    ax.set_title(f'{title} Comparison')
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(countries)
    ax.legend()

    plt.show(block=False) # from https://github.com/matplotlib/matplotlib/issues/12692/ to continue after the graph
    input() # to rectify the Github issue (https://github.com/matplotlib/matplotlib/issues/27389)
    #need to press enter here to continue


def get_safety_info(city, peace_index_data, temperature_data):
    country = get_country_for_city(city, temperature_data)

    #option to get safety info for the selected country
    if country:
        print(f"\nWould you like safety information for {country}?")
        user_choice = input("Enter 'yes' or 'no': ").lower()

        #if user selects yes, provide three years to retrieve safety info from
        if user_choice != 'no':
            print(f"\nWould you like the Global Peace Index (GPI) for {country} in 2021, 2022, or 2023?")
            year = input("Enter the year (2021, 2022, or 2023): ")

            #retrieve the GPI for the selected year
            if year in ['2021', '2022', '2023']:
                gpi_value = read_gpi_values(country, peace_index_data, year)
                if gpi_value is not None:
                    print(f"\nGlobal Peace Index (GPI) for {country} in {year}: {gpi_value}")
                    print(f"\n(note: lower GPI scores indicate a safer environment)")

                #if the GPI is not available, provide the user with a message
                else:
                    print(f"GPI information not found for {country} in {year}.")

            #if the user did not input a valid year option
            else:
                print("Invalid year. Please enter '2021', '2022', or '2023'.")

        #if the user did not want any safety data for their selected country
        # else: 
        #     print("Thank you. Have a great day!")

    #if the chosen city is not in the temperature data set
    else: 
        print("City not found. Please try again.")


#this function reads the GPI value from the csv file
def read_gpi_values(country, peace_index_data, year):
    gpi_values = {}
    with open(peace_index_data, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        for row in reader:
            if row[0].lower() == country.lower():
                try:
                    gpi_value = float(row[int(year) - 2021 + 1])
                    return gpi_value
                except (IndexError, ValueError):
                    return None

#this function provides the option to visualize the safety data 
def visualize_gpi(city, peace_index_data, temperature_data):
    country = get_country_for_city(city, temperature_data)
    if country:
        print(f"\nWould you like a visual representation of the Global Peace Index (GPI) for {country}?")
        visualize_choice = input("Enter 'yes' or 'no': ").lower()

        #if the user selects yes, visualize the GPI data for selected year
        if visualize_choice != 'no':
            print("\nChoose a year for visualization (2021, 2022, or 2023):")
            year = input("Enter the year: ")

            if year in ['2021', '2022', '2023']:
                visualize_gpi_bar_graph(country, peace_index_data, year)

            #once the graph visualises, press enter to continue

            #if the user selects an invalid year 
            else:
                print("Invalid year. Please enter '2021', '2022', or '2023'.")

        #if the user did not want to visualize the GPI data
        else:
            print("No worries!")
            prompt_restart_search()
    else:
        print("Country not found. Please try again.")

#this function visualizes the GPI data as a bar graph
def visualize_gpi_bar_graph(country, peace_index_data_file, year):
    countries = []
    gpi_values = []

    with open(peace_index_data_file, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        for row in reader:
            countries.append(row[0])
            try:
                gpi_values.append(float(row[int(year) - 2021 + 1]))
            except (IndexError, ValueError):
                gpi_values.append(None)

    visualize_bar_graph(country, countries, gpi_values, f'Global Peace Index ({year})')
    prompt_restart_search()


# this function asks the user if they want to restart their search
def prompt_restart_search():
    # ask the user if they want to restart the process
    choice = str(input("Are you happy with your search result? Enter 'yes' or 'no': "))
    # print discount code if happy with search result
    if choice != "no":
        print("""
        That's amazing! We're happy we could help :)
        Here is a coupon to get $30 off on your flight bookings: BRIAN30
        Goodbye!
        """)   
        exit(1)
    else:
    # if yes, take them to the main menu
        print("\n\nNo problem! Let's try again.\n\n")
        login_or_create()

login_or_create()