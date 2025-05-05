from setuptools import setup, find_packages

setup(
    name='daisy-pre-commit-hooks',
    version='0.1.0',
    description='Custom Odoo Pre-commit hooks',
    author='Your Name',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'check_duplicate_method_names = scripts.check_duplicate_method_names:main',
            'check_sql = scripts.check_sql:main',
            'check_for_return = scripts.check_for_return:main',
            'check_xml_header = scripts.check_xml_header:main',
            'check_xml_closing_tags = scripts.check_xml_closing_tags:main',
            'check_report_template = scripts.check_report_template:main',
            'check_compute_function = scripts.check_compute_function:main',
            'check_requirements = scripts.check_requirements:main',
            'check_print_usage = scripts.check_print_usage:main',
            'check_duplicate_ids = scripts.check_duplicate_ids:main',
            'check_sudo_comment = scripts.check_sudo_comment:main',
            'check_long_functions = scripts.check_long_functions:main',
            'check_model_file = scripts.check_model_file:main',
            'check_module_names = scripts.check_module_names:main',
            'check_xml_filenames = scripts.check_xml_filenames:main',
            'check_lines_max = scripts.check_lines_max:main',
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.7',
)
