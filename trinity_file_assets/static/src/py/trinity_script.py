import subprocess

def execute_commands():
    commands = [
        # Stop the Odoo service
        "sudo systemctl stop odoo18",

        # Copy primary_variables.scss
        "cp -f /opt/odoo18/custom/addons/trinity_file_assets/static/src/scss/primary_variables.scss /opt/odoo18/addons/web/static/src/scss/",

        # Copy primary_variables.scss
        "cp -f /opt/odoo18/custom/addons/trinity_file_assets/static/src/scss/control_panel.scss /opt/odoo18/addons/web/static/src/search/control_panel/",

        # Copy list_renderer.scss
        "cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/scss/list_renderer.scss /opt/odoo18/addons/web/static/src/views/list/",

        # Copy form_controller.scss
        "cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/scss/form_controller.scss /opt/odoo18/addons/web/static/src/views/form/",

        # Copy webclient_templates.xml
        "cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/xml/webclient_templates.xml /opt/odoo18/addons/web/views/",

        # Copy action_menus.xml
        "cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/xml/action_menus.xml /opt/odoo18/addons/web/static/src/search/action_menus/",

        # Copy cog_menu.xml
        "cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/xml/cog_menu.xml /opt/odoo18/addons/web/static/src/search/cog_menu/",

        # Copy cog_menu.xml
        "cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/xml/control_panel.xml /opt/odoo18/addons/web/static/src/search/control_panel/",

        # Copy each image file individually
cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/img/favicon.ico /opt/odoo18/addons/web/static/img/
cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/img/logo.png /opt/odoo18/addons/web/static/img/
cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/img/logo2.png /opt/odoo18/addons/web/static/img/
cp /opt/odoo18/custom/addons/trinity_file_assets/static/src/img/smiling_face.svg /opt/odoo18/addons/web/static/img/

        # Start the Odoo service
        "sudo systemctl start odoo18"
    ]

    for command in commands:
        try:
            print(f"Executing: {command}")
            subprocess.run(command, shell=True, check=True)
            print(f"Success: {command}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute: {command}\nError: {e}")

if __name__ == "__main__":
    execute_commands()

# sudo python3 /opt/odoo18/custom/addons/trinity_file_assets/static/src/py/trinity_script.py
# tail -f /var/log/odoo/odoo18.log
