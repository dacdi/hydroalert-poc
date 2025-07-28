from dotenv import load_dotenv
import os

load_dotenv()

TESTORTE_CSV = os.getenv("TESTORTE_CSV")
OUTPUT_CSV = os.getenv("OUTPUT_CSV")
