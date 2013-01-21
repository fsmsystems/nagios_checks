FSM - Nagios Checks
=============
--> Checks sin necesidad de instalar agentes nrpe, ssh o scripts locales

<u>XenServer check</u>
-----------------
Mediante la XenApi 'import XenAPI' el check para XenServer es capaz de analizar diferentes puntos, definidos por los parametros:<br><br>
- SR: Comprobar el estado de los PBDs conectados por I-SCSI por cada Host de cada SR <br>
- HOSTS: Verificar que el estado del host es 'enabled'<br>
- DISKS: Comprobar que ningún SR se quede sin espacio <br>
<br>
Simplemente con tener acceso desde el servidor Nagios al puerto https (443) es suficiente.

<u>Definición del comando</u>
-----------------------
define command{
<br>        command_name check_xen
<br>         command_line $USER1$/check_xen.py $ARG1$ root $ARG2$ $ARG3$ $ARG4$ $ARG5$
<br>         }

<u>Definición del servicio</u>
-----------------------
define service{
<br>        use                             C-XEN_HW
<br>        host_name                       SB-XENBOX_POOL 
<br>        service_description             SB-CLUSTER_HOSTS
<br>       check_command                   check_xen!masterhostip!passwd!HOSTS!0!0 
<br>        }

<br>define service{
<br>        use                             C-XEN_HW
<br>        host_name                       SB-XENBOX_POOL
<br>       service_description             SB-CLUSTER_STORAGE_PBDs
<br>       check_command                   check_xen!masterhostip!passwd!SR!0!0
<br>        }
<br>
<br>define service{
<br>        use                             C-XEN_HW
<br>        host_name                       SB-XENBOX_POOL
<br>        service_description             SB-SHARED_STORAGE_FREE
<br>        check_command                   check_xen!masterhostip!passwd!DISK!90!95
<br>        }
