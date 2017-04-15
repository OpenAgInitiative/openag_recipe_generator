import couchdb
import argparse
import json
import requests
import subprocess

def load_args():
    parser = argparse.ArgumentParser(description="Load recipes to couchdb instance",
                                     epilog="python load_recipe_to_server.py -u \"http://10.1.10.106:5984\" -r light_blue_red_72hours.json --start_recipe")
    parser.add_argument('-u', '--server_url', help='Couchdb Server: http://localhost:5984  (dont forget the http or port)')
    parser.add_argument('-r', '--recipe', help='Recipe json file path. It should be a proper json file.')
    parser.add_argument('-s', '--start_recipe', help='Start recipe after uploading it? (True/False) Default:False', action='store_true', default='store_false')
    args = parser.parse_args()
    return args.server_url, args.recipe, args.start_recipe


def validate_server_uri(server_uri):
    # Need to account for ending slash
    if not server_uri.startswith("http"):
        server_uri = "http://" + server_uri
    if not server_uri[-5] == ":":
        server_uri += ":5984"
    return server_uri


def load_recipe(file_name):
    with open(file_name, 'r') as f:
        data = json.load(f)
    return data


def save_to_server(server_uri, db_name, document):
    server = couchdb.Server(server_uri)
    db = server[db_name]
    db[document['_id']] = document


def start_recipe_on_server(server_uri, recipe_id):
    service_url = server_uri + "/_openag/api/0.0.1/service"
    api_url = service_url + "/environments/environment_1/start_recipe"
    print(api_url)
    #r = requests.post(api_url, params = recipe_id)
    # Not sure what format the post needs to be in...
    cmd_string = "curl -H 'Content-Type: application/json' \
                       -X POST {} \
                       -d \'[\"{}\"]\'".format(api_url, recipe_id)
    print(cmd_string)
    subprocess.call(cmd_string, shell=True)
    # assert r.status_code == "200"



def test_start_recipe_on_server():
    print(start_recipe_on_server("http://10.1.10.240:5984", "light_blue_red_72hours"))
    assert False

def main():
    server_uri, recipe_file_name, start_recipe = load_args()
    recipe_dict = load_recipe(recipe_file_name)
    db_name = "recipes"
    print("Uploading " + recipe_dict["_id"] + " ...")
    save_to_server(server_uri, db_name, recipe_dict)
    if start_recipe:
        print("Sending command to start recipe " + recipe_dict["_id"])
        start_recipe_on_server(server_uri, recipe_dict["_id"])


if __name__ == '__main__':
    main()
