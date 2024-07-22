import shutil
import os
import logging
from conversion import *
from htmlnode import *
from textnode import *
import re


logging.basicConfig(filename="/home/jallen/BootDev/StaticSiteGen/src/file_log.txt", level=1)
source_dir = "./static"
target_dir = "./public"
content_path = "./content"
template_path = "./template.html"

def main():
    print("Deleting public directory...")
    logging.info("Deleting public directory...")
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    
    print("Copying static files to public directory...")
    logging.info("Copying static files to public directory...")
    copy_files_recursive(source_dir, target_dir)

    generate_pages_recursive(content_path, template_path, target_dir)

def copy_files_recursive(source_dir_path, dest_dir_path):
    if not os.path.exists(dest_dir_path):
        os.mkdir(dest_dir_path)

    for filename in os.listdir(source_dir_path):
        from_path = os.path.join(source_dir_path, filename)
        dest_path = os.path.join(dest_dir_path, filename)
        print(f" * {from_path} -> {dest_path}")
        if os.path.isfile(from_path):
            shutil.copy(from_path, dest_path)
        else:
            copy_files_recursive(from_path, dest_path)

def extract_title(markdown):
    blocks = markdown.split("\n")

    for block in blocks:
        if block.startswith("# "):
            return block.lstrip("# ")
    raise Exception("No header provided")

def generate_page(from_path, template_path, target_path):
    print(f"Generating page from {from_path} to {target_path} using {template_path}")
    logging.info(f"Generating page from {from_path} to {target_path} using {template_path}")

    with open(from_path, "r") as file:
        md_contents = file.read()

    with open(template_path, "r") as file:
        template_contents = file.read()

    html_str = markdown_to_html_node(md_contents).to_html()
    title = extract_title(md_contents)
    final = fill_template(html_str, title, template_contents)

    if not os.path.exists(target_path):
        os.makedirs(target_path)

    full_path = os.path.join(target_path, "index.html")

    f = open(full_path, 'w')
    f.write(final)
    f.close()    

def fill_template(html_string, title, template):
    temp = template

    temp1 = temp.replace("{{ Title }}", title)
    temp2 = temp1.replace("{{ Content }}", html_string)

    return temp2

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    if os.path.isdir(dir_path_content):
        items = os.listdir(dir_path_content)
        for item in items:
            new_path_content = os.path.join(dir_path_content, item)
            new_path_dest = os.path.join(dest_dir_path, item)
            generate_pages_recursive(new_path_content, template_path, new_path_dest)
    elif os.path.isfile(dir_path_content):
        dest_path = os.path.dirname(dest_dir_path)
        generate_page(dir_path_content, template_path, dest_path)
    


main()