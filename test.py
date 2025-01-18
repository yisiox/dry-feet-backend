import yaml

with open("data/linkways.yaml", 'r') as infile:
    data = yaml.load(infile, Loader=yaml.Loader)
    print(data)
