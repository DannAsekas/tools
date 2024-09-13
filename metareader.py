from googlesearch import search
from duckduckgo_search import DDGS
import requests
from exiftool import ExifToolHelper
import os
import re

#Returns a list, parsed from a given input textfile with all the subdomains
def get_subdomain_list(filename):
    with open(filename, 'r') as filename:
        subdomains = filename.readlines()
    # trim possible whitespaces from subdomain names
    subdomains = [subdomain.strip() for subdomain in subdomains]
    print(subdomains)
    return subdomains

#Searches for X files where X is equal to max_results from a given subdomain and returns them in a list of urls
def get_resources(max_results,subdomain):
        #Crawl subdomains with google/ddg queries like: "site:dev.example.com filetype:pdf"
        query = "site:"+subdomain+" filetype:pdf" #actually manual input 
        print("Realizando la búsqueda... "+query)
        #results = search(query, num_results=2,sleep_interval=5) #Google search (isn't working)
        results = DDGS().text(query, max_results=max_results) #DDG search
        resources = []
        for link in results:
            resources.append(link['href'])
        return resources

#Gets a list that contains several urls
def save_files_to_disk(list,domain):
    try:
        #if extension is pdf, save in pdf directory
        for url in list:
            filename = url.split('/')[-1]
            if filename.lower().endswith('.pdf'):
                #Create a directory if it does not exist already for the given domain
                directory = './pdf/'+domain
                if not os.path.exists(directory):
                    #If not existant, create directory
                    os.makedirs(directory)
                response = requests.get(url)
                # if response OK
                if response.status_code == 200:
                    #save the file to disk
                    with open(directory+'/'+filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Archivo {filename}: Descargado exitosamente.")
                else:
                    print(f"Error al descargar el archivo {filename}")
    except Exception as e:
        print(f"Error al descargar el archivo: {filename}. Error: {str(e)}")

def read_metadata(file,mode):

    with ExifToolHelper() as et: #works the best and for all filetypes but requires exiftool installed
        #TODO: different verbose modes
        if mode == 'light':
            tags = ['FileName', 'Author', 'Producer','Creator']
        if mode == 'detailed':
            tags = ['FileName', 'Author', 'Producer','Creator','FileSize','FileAccessDate','ModifyDate']
        if mode == 'paranoic':
            tags = None

        if tags:
            for d in et.get_tags(file,tags=tags): 
                for k, v in d.items():
                    k = re.sub(r'^.*?\:', '', k)
                    print(f"{k} = {v}")
        else:
            for d in et.get_metadata(file): 
                for k, v in d.items():
                    k = re.sub(r'^.*?\:', '', k)
                    print(f"{k} = {v}")

def main(input_filename):
    for domain in get_subdomain_list(input_filename):
        print(f'Domain: {domain}')
        #save_files_to_disk(get_resources(5,domain),domain)

    for directory,dirs,files in os.walk('pdf'):
        for file in files:
            print(f"Metadata from {file}:")
            read_metadata(directory+"/"+file,'light')
            print("--------------")
        
if __name__ == '__main__':
    import sys
    
    #Si no se ha inputeado fichero de subdominios, devolver error
    if len(sys.argv) != 2:
        print("Uso: python script.py <nombre_archivo_subdominios>")
        sys.exit(1)
    
    main(input_filename = sys.argv[1])