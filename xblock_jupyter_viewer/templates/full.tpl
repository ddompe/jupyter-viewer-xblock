{%- extends 'basic.tpl' -%}

{%- block header -%}
<!DOCTYPE html>
<html>
    <head>
        {%- block html_head -%}
        <meta charset="utf-8" />
        {% set nb_title = nb.metadata.get('title', '') or resources['metadata']['name'] %}
        <title>{{nb_title}}</title>
        <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
        <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.0.4/css/all.css" integrity="sha384-DmABxgPhJN5jlTwituIyzIUk6oqyzf3+XuP7q3VfcWA2unxgim7OSSZKKf0KSsnh" crossorigin="anonymous">
        {% for css in resources.inlining.css[1:] -%}
            <style type="text/css">
            {{ css }}
            </style>
        {% endfor %}
        <style type="text/css">
            {{ resources.notebook_default_css }}
        </style>
        {%- endblock html_head -%}
    </head>
{%- endblock header -%}
