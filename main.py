# http://127.0.0.1:8000/bulk-data-paginated?page=1227&chunk_size=2022
# http://127.0.0.1:8000/bulk-data-paginated?page=1978&chunk_size=731
# http://127.0.0.1:8000/bulk-data
# pip install fastapi uvicorn sqlalchemy
# uvicorn main:app --host 127.0.0.1 --port 8000 --reload
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import os
import json
from sqlalchemy import create_engine, text

app = FastAPI()

# Database configuration (example)
DATABASE_URL = "sqlite:///database/bulk.db"  # Correct path to the database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

async def generate_file(chunk, chunk_number, output_folder='chunks'):
    """
    Processes and saves a chunk of data as a JSON file.

    This function creates a directory (if it doesn't exist) and saves the given 
    chunk of data to a file within that directory. The file is named `part_{chunk_number}.json`, 
    where `{chunk_number}` is the number provided.

    Args:
    - chunk (list): A list of data to be saved. It is expected to be a Python list of dictionaries or similar.
    - chunk_number (int): The number representing the chunk's order. This number will be used to name the output file.
    - output_folder (str, optional): The folder where the chunk file will be saved. Default is 'chunks'.

    Returns:
    - None: This function does not return anything. It directly saves the chunk to the disk.
    """

    # Check if the directory exists, if not, create it
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Generate the filename and save the chunk
    file_name = os.path.join(output_folder, f"part_{chunk_number}.json")
    with open(file_name, "w", encoding="utf-8") as file:
        # Directly write the chunk, since it's already a Python list
        json.dump(chunk, file, ensure_ascii=False, indent=4)

    # Get the absolute path of the file for the message
    full_path = os.path.abspath(file_name)

    # Print the processing message with the full path
    print(f"Processing and saving chunk number {chunk_number} into directory: {full_path}")

# Function to retrieve data in chunks of 100 records
async def get_large_data_chunks(chunk_size=1000):
    """
    This function fetches data from the `large_table` in chunks of the specified size (default: 100).
    Each chunk is sent as a JSON-encoded string.

    Args:
    - chunk_size (int): The number of records per chunk to fetch and send. Default is 100.

    Yields:
    - JSON-encoded string of a chunk of records.
    """
    
    query = "SELECT * FROM large_table LIMIT 10000"  # SQL query to fetch all records from the table
    with engine.connect() as connection:
        result = connection.execution_options(stream_results=True).execute(text(query))
        chunk = []  # Buffer to accumulate records for each chunk
        chunk_number = 1  # Chunk counter
        for row in result.mappings():  # Using mappings() to get records as key-value pairs
            chunk.append(dict(row))  # Append each row to the buffer
            if len(chunk) >= chunk_size:  # When the buffer reaches the specified chunk size
                yield json.dumps(chunk) + "\n"  # Yield the chunk as a JSON string
                print('Sent chunk', chunk_number)
                await generate_file(chunk, chunk_number, output_folder='chunks')  # async call
                chunk_number += 1
                chunk = []  # Clear the buffer
                
        if chunk:  # Send remaining records if any
            yield json.dumps(chunk) + "\n"
        print("All data has been sent")  # Final message when all data has been sent

@app.get("/bulk-data")
async def get_bulk_data():
    """
    Endpoint that streams large data in chunks from the database.

    Returns:
    - StreamingResponse: Streams the data in JSON format as a series of chunks.
    """
    return StreamingResponse(get_large_data_chunks(), media_type="application/json")

async def get_data_paginated(page: int, chunk_size: int):
    """
    This function retrieves records from `large_table` based on the page number and chunk size.

    Args:
    - page (int): The page of data to retrieve (1-based).
    - chunk_size (int): The number of records per page (chunk size).

    Yields:
    - JSON-encoded string of a chunk of records.
    """
    # Calculate the offset (how many records to skip)
    offset = (page - 1) * chunk_size

    query = f"SELECT * FROM large_table LIMIT {chunk_size} OFFSET {offset}"

    with engine.connect() as connection:
        result = connection.execution_options(stream_results=True).execute(text(query))
        chunk = []  # Buffer to accumulate records
        chunk_number = 1
        for row in result.mappings():  # Use mappings() to get records as key-value pairs
            chunk.append(dict(row))

        if chunk:
            yield json.dumps(chunk) + "\n"  # Yield the chunk as a JSON string
            await generate_file(chunk, chunk_number, output_folder='chunks_paginated')  # async call
            chunk_number += 1
        else:
            yield json.dumps({"message": "No more data available"}) + "\n"  # Message if no more data

@app.get("/bulk-data-paginated")
async def get_bulk_data(page: int = 1, chunk_size: int = 100):
    """
    Endpoint to retrieve paginated data chunks from the `large_table`.

    Args:
    - page (int): The page number to retrieve. Default is 1.
    - chunk_size (int): The chunk size (number of records per page). Default is 100.

    Returns:
    - A StreamingResponse with the data in JSON format.
    """
    if page < 1 or chunk_size < 1:
        raise HTTPException(status_code=400, detail="Page and chunk_size must be greater than 0")
    
    return StreamingResponse(get_data_paginated(page, chunk_size), media_type="application/json")

@app.get("/count-records")
async def count_records():
    """
    Endpoint to count the total number of records in the `large_table`.

    Returns:
    - JSON: The total number of records in the table.
    """
    with engine.connect() as connection:
        result = connection.execute(text("SELECT COUNT(*) FROM large_table"))
        total_records = result.scalar()  # Get the count of records
    return {"total_records": total_records}