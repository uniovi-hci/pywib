Introduction
============

Welcome to **pywib** (Python Web Interaction Behaviour) the python library designed to help ease the analysis of user interaction data in the field of HCI (Human-Computer Interaction).

This project aims to analyze user interaction with web applications by processing interaction event data (such as clicks, mouse movements, scrolls, etc.) recorded by researchers to aid their studies.

It provides tools to compute various interaction related metrics (like velocity, acceleration, auc, etc.) and other useful functionalities to facilitate the analysis of user behavior, such as stroke visualization or video generation of user sessions.

Rationale
=============
The analyisis of mouse interaction has been widely used in HCI to infer in several aspects of the users interaction with the system.
This mouse dynamics have been proven useful for analysing bheavioral patterns :cite:p:`Katerina2018-ch,Cepeda2018-kn`, 
cognitive and physicial conditions affecting the user :cite:p:`Seelye2015-yxm, Khan2008-is, Rhim2023-uz` 
or even for user identification :cite:p:`Karim2020-ss` and authentication :cite:p:`Monrose-2000-oc`.

One could enumerate hundreads of research works in this field that have analyzed mouse interaction data to extract meaningful insights about user behavior.
However, there is a lack of dedicated tools and libraries to facilitate this analysis, which is a gap that **pywib** aims to address.

As of 2026, there are no other Python libraries specifically designed for analyzing web interaction behavior in HCI research.
While there are libraries for this same purpose in other programming languages, such as R's `mousemove` :cite:p:`Wulff2025-bt`, 
they may not be as accessible to researchers who primarily use Python for data analysis and machine learning tasks, limiting as well
the integration with other Python-based tools and libraries commonly used in HCI research or the automation of analysis pipelines using Python based APIs.

Validity of Metrics
--------------------
One of the main problems when dealing with a library that aims to cover computation of, at most, the most common metrics in HCI research is the validity of such ones.
For this reason, **pywib** has been developed taking into account the most relevant metrics used in research works, that have been proven to be representative of user behavior in different contexts.
This does not mean that the developer team will not expand the library with new metrics in the future, if there is a given need for them, but rather that the initial set of metrics that have been included are those that could be initialy proven to be mathematically and experimentally valid.

Context Specific Metrics
~~~~~~~~~~~~~~~~~~~~~~~~~~~
It is important to note that not all metrics are equally valid in all contexts.
For example, metrics that are valid for analyzing mouse movements in a desktop web application may not be valid for analyzing touch interactions on mobile devices.
Therefore, it is crucial to consider the context in which the metrics will be applied and to validate them accordingly.

Moreover, the setup of an experiment itself can influence the validity of certain metrics :cite:p:`Schoemann2019-vv,Kuric2024-wc`, which is why **pywib** encourages users to validate the metrics they compute in their specific context and experiment setup.

Installation
-------------
You can install **pywib** using pip:

.. code-block:: bash

   pip install pywib

Getting Started
-----------------

I suggest you take a deep look at rest of the documentation, such as the `Keyboard Interaction Metrics <keyboard.html>`_ or `Movement Interaction Metrics <movement.html>`_ sections in order to understand the different metrics that can be computed with **pywib** and find those that suit your research.

After that, you can check the `API Reference <api/index.html>`_ for more detailed information about the available functions and classes.

Small Example
~~~~~~~~~~~~~~
.. code-block:: python

   from pywib import velocity, velocity_metrics

   # From an already read DataFrame from a csv
   df_all_sessions = process_csv(input_file)
   df_all_sessions.rename(columns={'moveX': 'x', 'moveY': 'y', 'id_usuario': 'sessionId'}, inplace=True)

   vel = velocity(df_all_sessions)
   vel_metrics = velocity_metrics(vel)

   acc = acceleration(vel, None, True)

References
=============

.. bibliography:: references.bib
   :style: apa