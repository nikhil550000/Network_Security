from setuptools import setup, find_packages
from typing import List

def get_requirements()->List[str]:
    """
    This function will return list of requirements
    """
    requirement_list:List[str]  = []


    try:

        with open('requirements.txt','r') as file:
            lines = file.readlines()

            for line in lines:

                requirement = line.strip()

                if requirement and requirement!= '-e .':
                    requirement_list.append(requirement)

    except FileNotFoundError:
        print("requirements.txt file not found.")


    return requirement_list

print(get_requirements())

setup(
    name = "networkS,ecurity",
    version = "0.0.1",
    author = "nikhil sai",
    author_email = "nikhilsai550000@gmail.com",
    packages = find_packages(),
    install_requires = get_requirements()
)