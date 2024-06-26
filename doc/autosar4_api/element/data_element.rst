.. _ar4_element_DataElement:

DataElement
===========

.. table::
   :align: left

   +--------------+------------------------------------------------------+
   | XML tag      | <DATA-ELEMENT>                                       |
   +--------------+------------------------------------------------------+
   | Module       | autosar.element                                      |
   +--------------+------------------------------------------------------+
   | Inherits     | :ref:`autosar.element.Element <ar4_element_Element>` |
   +--------------+------------------------------------------------------+

DataElements are commonly used in :ref:`ar4_portinterface_SenderReceiverInterface` but they sometimes are used for other purposes.

Constructor
-----------

..  py:method:: DataElement(name, typeRef, [isQueued = False], [swAddressMethodRef = None], [swCalibrationAccess = None], [swImplPolicy = None], [category = None], [parent = None], [adminData = None])

    :param str name: Short-name identifer
    :param str typeRef: Type reference
    :param bool isQueued: Queued property
    :param str swAddressMethodRef: Reference to SoftwareAddressMethod
    :param str swCalibrationAccess: Calibration access setting
    :param str swImplPolicy: Implementation policy
    :param str category: Category string
    :param parent: Only used internally (leave as None)
    :param adminData: Optional AdminData object

swCalibrationAccess
~~~~~~~~~~~~~~~~~~~

.. table::

    +------------------------------+------------------------------------------------------------------------------------------------+
    | Value                        | Description                                                                                    |
    +==============================+================================================================================================+
    | :literal:`None`              | No calibration access set                                                                      |
    +------------------------------+------------------------------------------------------------------------------------------------+
    | :literal:`""` (Empty string) | Create default calibration access value                                                        |
    |                              | as set by Workspace.profile.swCalibrationAccessDefault                                         |
    +------------------------------+------------------------------------------------------------------------------------------------+
    | :literal:`"NOT-ACCESSIBLE"`  | The element will not be accessible by external tools                                           |
    +------------------------------+------------------------------------------------------------------------------------------------+
    | :literal:`"READ-ONLY"`       | Read only access                                                                               |
    +------------------------------+------------------------------------------------------------------------------------------------+
    | :literal:`"READ-WRITE"`      | Read-write access                                                                              |
    +------------------------------+------------------------------------------------------------------------------------------------+

swImplPolicy
~~~~~~~~~~~~

.. table::

    +--------------------------------+-----------------------------------------------------------------------------------------+
    | Value                          | Description                                                                             |
    +================================+=========================================================================================+
    | :literal:`None`                | No policy set                                                                           |
    +--------------------------------+-----------------------------------------------------------------------------------------+
    | :literal:`"CONST"`             | Prevent implementation to modify the memory. Uses the "const" modifier in C.            |
    +--------------------------------+-----------------------------------------------------------------------------------------+
    | :literal:`"FIXED"`             | Data element is fixed and might be implemented as in place data such as a #define.      |
    +--------------------------------+-----------------------------------------------------------------------------------------+
    | :literal:`"MEASUREMENT-POINT"` | Data element is created for measurement purposes only.                                  |
    +--------------------------------+-----------------------------------------------------------------------------------------+
    | :literal:`"QUEUED"`            | Data element is queued and has event semantics. Data is processed in FIFO order.        |
    +--------------------------------+-----------------------------------------------------------------------------------------+
    | :literal:`"STANDARD"`          | Data element is non-queued and uses the "last is best" semantics                        |
    +--------------------------------+-----------------------------------------------------------------------------------------+

Attributes
-----------

For inherited attributes see :ref:`autosar.element.Element <ar4_element_Element>`.

..  table::
    :align: left

    +--------------------------+-------------------+-----------------------------------------------------+
    | Name                     | Type              | Description                                         |
    +==========================+===================+=====================================================+
    | **dataConstraintRef**    | None or str       | <DATA-CONSTR-REF>                                   |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **isQueued**             | bool              | <IS-QUEUED>                                         |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **swAddressMethodRef**   | None or str       | <SW-DATA-DEF-PROPS><SW-ADDR-METHOD-REF>             |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **swCalibrationAccess**  | None or str       | <SW-DATA-DEF-PROPS><SW-CALIBRATION-ACCESS>          |
    +--------------------------+-------------------+-----------------------------------------------------+
    | **typeRef**              | str               | <TYPE-TREF>                                         |
    +--------------------------+-------------------+-----------------------------------------------------+

.. note::

    It might be better idea to change DataElement to have a single instance of autosar.base.SwDataDefPropsConditional.
    This will remove some duplicated attributes found in this class.


Properties
----------

..  table::
    :align: left

    +--------------------------+-------------------+------------------------------------------------------+
    | Name                     | Type              | Access Type | Description                            |
    +==========================+===================+=============+========================================+
    | **swImplPolicy**         | None or str       | Get, Set    | <SW-DATA-DEF-PROPS><SW-IMPL-POLICY>    |
    +--------------------------+-------------------+-------------+----------------------------------------+

Public Methods
--------------

* :ref:`ar4_element_DataElement_setProps`

Method Description
------------------

.. _ar4_element_DataElement_setProps:

setProps
~~~~~~~~

.. py:method:: DataElement.setProps(props)

    :param props: Properties object
    :type props: autosar.base.SwDataDefPropsConditional

    Updates the following attributes/properties from the given props object

    * dataConstraintRef
    * swAddressMethodRef
    * swCalibrationAccess
    * swImplPolicy
