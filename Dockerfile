FROM python:3.10

# Instala dependencias
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt1-dev \
    libldap2-dev \
    libsasl2-dev \
    libjpeg-dev \
    zlib1g-dev \
    libjpeg8-dev \
    liblcms2-dev \
    libblas-dev \
    libatlas-base-dev \
    libffi-dev \
    libssl-dev \
    libfreetype6-dev \
    libwebp-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libxcb1-dev

# Copia Odoo (si ya lo descargaste en /odoo)
COPY ./odoo /opt/odoo
WORKDIR /opt/odoo

# Instala dependencias de Odoo
COPY requirements.txt .
RUN pip install -r requirements.txt

# Expone el puerto
EXPOSE 8069

# Comando de inicio
CMD ["./odoo-bin", "--addons-path=addons,custom_addons"]
