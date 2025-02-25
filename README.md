# Bulk Data Streaming API with FastAPI

This FastAPI application provides endpoints for streaming bulk data from a database in paginated chunks or all at once. It supports two modes:

1. Streaming data in chunks without pagination.
2. Streaming paginated data based on specified page and chunk sizes.

### Features:
- Streams large datasets from an SQL database (SQLite in this example).
- Supports both non-paginated and paginated data streaming.
- Asynchronously saves data chunks as JSON files to disk.
- Provides an endpoint to count the total number of records in the database.

### Prerequisites

- Python 3.x
- FastAPI
- Uvicorn
- SQLAlchemy (SQLite used for this example)

### Installation

To get started with this project, first, install the required dependencies using `pip`:

```bash
pip install fastapi uvicorn sqlalchemy
```

### Running the Application

To run the FastAPI application, use the following command:

```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

This will start the server locally at `http://127.0.0.1:8000`.

Alternatively, to make the application accessible externally, use:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Endpoints

#### 1. `/bulk-data` - Stream All Data in Chunks

This endpoint streams the bulk data from the database in chunks.

- **Method**: `GET`
- **URL**: `/bulk-data`
- **Response**: A `StreamingResponse` that streams the data in JSON format, divided into chunks.

Example Request:

```bash
http://127.0.0.1:8000/bulk-data
```

#### 2. `/bulk-data-paginated` - Stream Paginated Data

This endpoint allows you to stream data in paginated chunks. You can specify the page number and the chunk size.

- **Method**: `GET`
- **URL**: `/bulk-data-paginated?page={page}&chunk_size={chunk_size}`
- **Query Parameters**:
  - `page`: The page number (1-based). Default is `1`.
  - `chunk_size`: The number of records per chunk. Default is `100`.

Example Requests:

```bash
http://127.0.0.1:8000/bulk-data-paginated?page=1227&chunk_size=2022
http://127.0.0.1:8000/bulk-data-paginated?page=1978&chunk_size=731
```

#### 3. `/count-records` - Get Total Record Count

This endpoint retrieves the total number of records in the database table.

- **Method**: `GET`
- **URL**: `/count-records`
- **Response**: A JSON object with the total number of records.

Example Request:

```bash
http://127.0.0.1:8000/count-records
```

### Code Breakdown

#### Database Configuration

The application is configured to use SQLite. The database URL is defined as:

```python
DATABASE_URL = "sqlite:///database/bulk.db"
```

Make sure that your database file exists and is accessible from the application.

#### Streaming Data

The data is retrieved in chunks, with each chunk being saved to disk as a JSON file. The `generate_file` function handles this task:

```python
async def generate_file(chunk, chunk_number, output_folder='chunks'):
    ...
```

The application uses the `get_large_data_chunks` and `get_data_paginated` functions to retrieve the data from the database and stream it.

#### Pagination

For paginated data, the `get_data_paginated` function calculates the correct offset based on the page number and chunk size:

```python
async def get_data_paginated(page: int, chunk_size: int):
    ...
```

#### Saving Data to Files

As the data is streamed, each chunk is saved into a separate file in the specified output folder (`chunks` for non-paginated, `chunks_paginated` for paginated).

```python
await generate_file(chunk, chunk_number, output_folder='chunks')
```

### Example Requests

Here are some example requests you can make to the API:

1. **Stream all data in chunks**:
   ```bash
   http://127.0.0.1:8000/bulk-data
   ```

2. **Stream paginated data (page 1227, chunk size 2022)**:
   ```bash
   http://127.0.0.1:8000/bulk-data-paginated?page=1227&chunk_size=2022
   ```

3. **Get total record count**:
   ```bash
   http://127.0.0.1:8000/count-records
   ```

### Notes

- The `generate_file` function writes each chunk to a separate JSON file in the `chunks` or `chunks_paginated` folder, depending on whether the data is being streamed paginated or not.
- The SQLite database used in the example is configured with `check_same_thread: False` to avoid thread-related issues during asynchronous calls.
- You may need to adjust the database configuration (`DATABASE_URL`) based on the actual path and database type you're using.

### Conclusion

This FastAPI application provides a simple and efficient way to stream large datasets from a database in chunks. The asynchronous design ensures that the application can handle large volumes of data without blocking the main thread, making it suitable for real-time data streaming scenarios.

---