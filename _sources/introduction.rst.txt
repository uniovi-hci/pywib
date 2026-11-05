Introduction
============

Welcome to **PyWIB** (Python Web Interaction Behaviour) the python library designed to help ease the analysis of user interaction data in the field of HCI (Human-Computer Interaction).

This project aims to analyze user interaction with web applications by processing interaction event data (such as clicks, mouse movements, scrolls, etc.) recorded by researchers to aid their studies.

It provides tools to compute various interaction related metrics (like velocity, acceleration, auc, etc.) and other useful functionalities to facilitate the analysis of user behavior, such as stroke visualization or video generation of user sessions.

Rationale
---------
The analyisis of mouse interaction has been widely used in HCI to infer in several aspects of the users interaction with the system.
This mouse dynamics have been proven useful for analysing behavioral patterns :cite:p:`Katerina2018-ch,Cepeda2018-km`, 
cognitive and physicial conditions affecting the user :cite:p:`Seelye2015-yx, Khan2008-is, Rhim2023-uz` 
or even for user identification :cite:p:`Karim2020-ss` and authentication :cite:p:`Monrose2000-oc`.

One could enumerate hundreds of research works in this field that have analyzed mouse interaction data to extract meaningful insights about user behavior.
However, there is a lack of dedicated tools and libraries to facilitate this analysis, which is a gap that **PyWIB** aims to address.

As of 2026, there are no other Python libraries specifically designed for analyzing web interaction behavior in HCI research.
While there are libraries for this same purpose in other programming languages, such as R's `mousemove` :cite:p:`Wulff2025-bt`, 
they may not be as accessible to researchers who primarily use Python for data analysis and machine learning tasks, limiting as well
the integration with other Python-based tools and libraries commonly used in HCI research or the automation of analysis pipelines using Python based APIs.

Cite us!
--------------------
PyWIB was presented on the `IARIA Congress 2026 <https://www.iaria.org/conferences2026/IARIACongress26.html>`__ and published in the proceedings of the conference, obtaining a `Best Paper Award <https://www.iaria.org/conferences2026/awardsIARIACongress26/congress2026_a4.pdf>`__.
If you use PyWIB in your research, we kindly ask you to cite us: :cite:p:`CarvajalAza2026PyWIB`


Validity of Metrics
--------------------
One of the main problems when dealing with a library that aims to cover computation of, at most, the most common metrics in HCI research is the validity of such ones.
For this reason, **PyWIB** has been developed taking into account the most relevant metrics used in research works, that have been proven to be representative of user behavior in different contexts.
This does not mean that the developer team will not expand the library with new metrics in the future, if there is a given need for them, but rather that the initial set of metrics that have been included are those that could be initialy proven to be mathematically and experimentally valid.

Context Specific Metrics
--------------------
It is important to note that not all metrics are equally valid in all contexts.

For this reason, **PyWIB** provides documentation on the validity and consideration of metrics affected by experimental contexts under the `Context Specific Metrics <context_specific_metrics.html>`__ section.

Installation and Getting Started
================================
You can install **PyWIB** using pip:

.. code-block:: bash

   pip install pywib

Understanding PyWIB
-------------------

We suggest you take a deep look at rest of the documentation, such as the `Keyboard Interaction Metrics <keyboard.html>`__ or `Movement Interaction Metrics <movement.html>`__ sections in order to understand the different metrics that can be computed with **PyWIB** and find those that suit your research.

In order to be consistent with PyWIB's data structure, we recommend checking out the `Data Structure <data_structure.html>`__ and the `Constants <constants.html>`_ _sections to understand how to properly format your data and use the provided constants for column names.

Another key element of PyWIB is the `Segmentation <segmentation.html>`_ _section, which explains how to segment your data into traces for more accurate metric computation. Most metrics are designed to operate on traces, so understanding how to segment your data is crucial for obtaining valid results.

After that, you can check other metrics specifications or the `API Reference <api/index.html>`_ _for more detailed information about the available functions and classes.

Getting to the code
-------------------

After you have familiarized yourself with the library and found the metrics that best suit your experiment, you can start using it in your own projects. 

Below is a simple example of how to use **PyWIB** to compute velocity metrics and visualize a trace.

.. code-block:: python

   from pywib import to_pywib_df, velocity, velocity_metrics, visualize_trace, ColumnNames

   # Considering an already loaded CSV into a pandas DataFrame

   df = to_pywib_df(df, "sessionIdCol", "xCoordinateCol", "yCoordinateCol", "timeStampCol", "eventTypeCol", "keyValueCol", "keyCodeCol").copy()

   v = velocity(df, per_traces=True)
   v_metrics = velocity_metrics(df=None, traces=v)

   userSession = df[df[ColumnNames.SESSION_ID] == "USER_A"].copy()
   visualize_trace(userSession, userSession.index, "USER_A", type="info", save_path="user_a_trace.png")

References
----------

.. bibliography:: references.bib
   :style: apa