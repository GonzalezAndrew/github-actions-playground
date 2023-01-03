import json

def update_image_tag():
    """Update image_tag variable in inputs.tfvars.json file.
    """    
    with open("inputs.tfvars.json", 'r') as fin:
        data = json.load(fin)
    fin.close()

    if data['image_tag']:
        latest_image_version = data['image_tag']
        version_split = latest_image_version.split(".")
        version_split[-1] = str(int(version_split[-1]) + 1)
        updated_version = ".".join(version_split)
        print(updated_version)

        data['image_tag'] = updated_version

        with open("inputs.tfvars.json", "w") as fout:
            json.dump(data, fout, indent=4)
        fout.close()
    else:
        raise Exception("The inputs.tfvars.json file does not contain the variable image_tag. Please pass the correct tfvars file!")