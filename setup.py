from setuptools import setup

setup(name='jtac-autoget-support',
      version='1.2',
      description='Gather RSI (request support information) and /var/log/* from JUNOS for JTAC Case',
      url='https://github.com/solotronics/jtac-autoget-support',
      author='Ansel Gene Gaddy',
      author_email='gene.gaddy@ibm.com',
      license='MIT',
      packages=['jtac-autoget-support'],
      install_requires=[
          'netmiko',
          'scp',
          'paramiko',
          'pysftp'
      ],
      zip_safe=False)
