FROM odoo:17.0

USER root

# Copia tus addons personalizados
COPY ./custom_addons /mnt/custom_addons

# Establece permisos
RUN chown -R odoo /mnt/custom_addons

USER odoo
