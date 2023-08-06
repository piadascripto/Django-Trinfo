import csv
import logging
import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand

logging.basicConfig(level=logging.INFO)

def connection_interactive_brokers(IBKR_user_token, IBKR_user_query):

	def fetch_page_content(url):
		try:
			response = requests.get(url)
			response.raise_for_status()  # Check for any HTTP errors
			return response.content, None
		except requests.HTTPError as http_err:
			error_msg = f"HTTP error occurred: {http_err}"
			logging.error(error_msg)
			return None, error_msg
		except Exception as err:
			error_msg = f"An error occurred: {err}"
			logging.error(error_msg)
			return None, error_msg
	
	def remove_duplicate_rows(input_file, output_file):
		with open(input_file, 'r') as infile:
			reader = csv.reader(infile)
			
			unique_rows = set()
			with open(output_file, 'w', newline='') as outfile:
				writer = csv.writer(outfile)
				
				for row in reader:
					row_tuple = tuple(row)
					if row_tuple not in unique_rows:
						writer.writerow(row)
						unique_rows.add(row_tuple)
	
	def fetch_IBKR_orders():
		url = f"https://www.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest?t={IBKR_user_token}&q={IBKR_user_query}&v=2"
		page_content, error = fetch_page_content(url)
		if error:
			logging.error(f"Error fetching IBKR data: {error}")
			return
		soup = BeautifulSoup(page_content, "html.parser")
		IBKR_code = soup.find("code").text.strip() if soup.find("code") else None
		if IBKR_code:
			user_query_url = f"https://www.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement?q={IBKR_code}&t={IBKR_user_token}&v=2"
			print(user_query_url)
			IBKR_user_orders, error = fetch_page_content(user_query_url)
			if not error and IBKR_user_orders:				
				# Write the data to the CSV file
				raw_orders_file = "raw_orders.csv"
				with open(raw_orders_file, 'wb') as file:
					file.write(IBKR_user_orders)
				# Clean the CSV file to remove duplicate headers
				orders_file = "orders.csv"
				remove_duplicate_rows(raw_orders_file, orders_file)
				print("===Successfully fetched orders from IBKR===")
			else:
				print("Error fetching user orders.")
		else:
			logging.error("Error fetching IBKR code.")

	fetch_IBKR_orders()


#review here for reusability 
class Command(BaseCommand):
	help = 'Fetches data from Interactive Brokers Flex Queries'
	def handle(self, *args, **kwargs):
		IBKR_user_token = kwargs.get('IBKR_user_token', IBKR_user_token)
		IBKR_user_query = kwargs.get('IBKR_user_query', IBKR_user_query)
		connection_interactive_brokers(IBKR_user_token, IBKR_user_query)
