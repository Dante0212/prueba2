FROM odoo:16.0

USER root
RUN pip3 install --upgrade pip

# Copia solo tu módulo personalizado
COPY ./custom_addons /mnt/extra-addons

USER odoo
