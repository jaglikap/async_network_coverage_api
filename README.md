## Asynchronous Network Operators Coverage API
This API serves to retrieve the nearest network towers withing their network coverage for given postal addresses in France.

### Technical information
- The project is developed using Python 3.11 and in PyCharm Community Version IDE 
### Installation 
- Clone the repository with git
- Create your virtual environment, I did it with venv
- In the root repository, launch the following pip command to install the dependencies
- ```
  pip install -r requirements.txt
  ```
- Launch the uvicorn server on a localhost port, I did it on 8080
- ```
  uvicorn app.main:app --reload --port 8080
  ```
### Getting familiar with mobile network coverage
- I did some research in order to understand how the basic mobile network coverage works.
### Explanation of the implementation of the solution
- The provided csv file `2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93_ver2.csv` contains more than 77K lines. If I opted to read it via simple python csv reader, or import it into a sql database, it would have costed in performance with slowness.
- I have opted for a preprocessing of the csv file via the **pandas** and **dask** libraries for operations on larger-than-memory datasets:
  - Firstly, we need to convert the lambert93 format of the coordinates into GPS format. This step is done by a standalone python script, `standalone/treat_tower_data.py` and a new csv file is generated `2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_GPS.csv`.
  - This new file, at the startup of the backend API is pickled via pandas.to_pickle method into the destination repository of the project `public/`, after the file's content is charged into a pandas.DataFrame. Remember to remove the serialized object file it if you plan to regenerate a new csv file (with the same header) if ever the data has changed.
  - How did I generate the conversion data from lambert93 into GPS coordinates:
    - Navigate in the root folder of the project (make sure that your virtual env is activated) and launch the following python command:
      - `python stand_alone/treat_tower_data.py --destfilename 2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_GPS.csv`
      - This generated the csv file in the following directory `public/`
- What happens when you send a post request to the endpoint of `/search` with some addresses ?
  - Firstly, there's a retrieval of the gps coordinates for each address by interrogation of the API Adresse (destined for the French mainland addresses)
  - Once we get the GPS coordinates, the process of calculation of the nearly located network towers can start
    - In this part, the network towers coverage data is loaded into a pandas.DataFrame object
    - Next, the network towers data is grouped by network operator, which means that at the end the network coverages for each network operator will be proposed.
    - In order to be able to find the nearly located network towers, I have opted to use an approach of spatial index in 2-dimension, by using a binary tree `KDTree` proposed by the library `scipy` to be able to do the searches.
      - The use of such spatial binary tree offers the possibility to find efficiently the k-nearest neighbours of, in our case, 2-dimensional coordinates (longitude, latitude). 
      - In this case, I have decided to propose the 3 nearest network towers for each network operator in order to offer an optimal connection
