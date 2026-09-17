Mouse Behavioral Patterns
=========================

Introduction
------------

In the context of HCI, mouse behavioral patterns refer to the combination of mouse movements, clicks and general interaction that can be explained or associated with specific user behaviors, cognitive states or activities while interacting with a computer interface.
This patterns have been identified in various studies analyzing user interaction with web pages, applications and forms, but a formal "catalog" of such patterns can not be found easily in the literature, therefore this section aims to summarize those patterns thathave been identified and described in previous research works to help researchers in the field of HCI better understand and analyze user behavior.

Original text from cite:`Katerina2018-ch`.

*In the area of HCI researchers have been trying to quantify the movement of humans who perform pointing tasks on computers and other devices. Mouse cursor movement is a vital part in this field and has been used in many studies.*

*In 2001, Mueller and Lockerd proposed the use of cursor patterns behavior as input to deliver personalized content to users. Unfortunately, the identification of patterns has not significantly advanced since then. Mouse patterns characterization is generally vague, and their identification remains a largely visual process and qualitative analysis.*

*There are not many research works that clearly attempt to detect users' behavioral attributes via mouse behavior. Such as...*

*There are several studies that have identified some common patterns of cursor movements, such as reading patterns, direct movements, random movements, hesitation patterns, fixed and guide patterns. These patterns have been identified in different web contexts like search engine result page, interaction with web forms and web site navigation. These works are of significant HCI contribution, since identifying mouse behavioral patterns allow us to infer the activity performed by the user, for example, usability problems and user experience*

Straight pattern
----------------
Described by `(Lee & Chen, 2006) <https://link.springer.com/chapter/10.1007/978-3-540-73287-7_59>`_.

Also known as the 'direct mouse movements' refers to users confident movements, characteried by a pause before a direc movement towards a target since "once traced the desired featre users move the mouse straight to it" (Lee & Chen, 2006)

According to `Rodden et al. (2008) <https://doi.org/10.1145/1358628.1358797>`_
, this pattern defines direct movements that occur once the user has decided which action to take and this could reveal certainty and task-oriented self-efficacy.

Hence, drawing from the related literature review, mouse trajectory (e.g. straight lines) or selected targets (i.e. clicks) after direct movements may measure the end-user's self-efficacy level or perceived ease of use when interacting with computer applications.

Hesitation pattern
------------------
First explicitly defined in Cheese project (Mueller & Lockerd, 2001, pp. 1–2).

According to the authors “hesitation on links or text could potentially provide information about what else interests the user on the page”. This hesitation could be expressed by the cursor as a mouse hover over the under decision item (i.e. element to click).

Other studies which focused on the analysis of movements of the cursor in web forms refer to the pattern of hesitation as movements between “two or more answers while trying to decide which one to choose (Ferreira et al., 2010). Hesitation patterns have also been identified during interaction with navigation menus (Atterer et al., 2006).

In commercial applications of mouse tracking, as ClickTale (2006), the pattern of hesitation is defined as “the average time from the beginning of a mouse hover to the moment of the mouse click”.

Hesitation pattern could hence be used to infer users’ perceived difficulty, risk-perception levels (since the user evaluates the cost benefits of choosing an action among others), or even the perceived usability from his/her interaction with the system.

Reading pattern
---------------
The reading pattern can be divided into two different types of behavior: the horizontal reading pattern that is characteristic but not so common among users (Rodden et al., 2008) and the vertical reading pattern where the mouse path traces a vertical line, with small or large pauses.

The vertical reading pattern is defined as a movement of “following the eye vertically” (Rodden et al., 2008). This pattern is observable in vertical lists like a menu where the users “use the mouse as a marker when they are looking through a list of links” (Mueller & Lockerd, 2001, pp. 1–2).

Random and fixed pattern
------------------------
According to Ferreira et al. (2010) the random pattern is characterized by movements “without any specific intention, just playing around and doing random movements whit short pauses or not”. The authors noted that the random movements often arise when the difficulty level of the task increases.
Hence, on presence of a random pattern we can infer doubt, difficulty, low self-efficacy, anxiety, etc.

Described in Lee and Chen (2006), the fixed pattern refers to the areas where the users mostly used for “repose” the cursor. For Lee and Chen (2006) these areas usually are on the right-side of the page. This area is also mentioned as “White space” (Ferreira et al., 2010) and research indicates that a large number of users use whitespace to rest the mouse, thus avoiding accidentally clicking a link.

Fixed pattern could be expressed via long or shorter mouse pauses on ‘neutral’ web-page areas. During this time users may reflect on the task, read (eye tracking could only reveal reading behavior during mouse pauses) or evaluate the costs and benefits of making particular decisions (e.g. clicks, actions). Hence, fixed pattern could measure risk-perception or usefulness levels.

Guide Pattern
-------------
Defined in Lee and Chen (2006), the guide pattern defines a behavior of continuous movement of the cursor. According to the authors this pattern seems to reflex an “exploratory” role that suggests a relationship between mouse and eye movement” and hence this pattern may give us an idea of the user expectations. Hence, guide pattern may be associated with users’ acceptance, i.e. perceived usefulness and ease of use and also willingness to learn.

However, guide pattern is very similar to the reading pattern since it can be expressed via ‘smooth’ (i.e. slow) cursor movements identifying horizontal or vertical reading.

Keystroke dynamics in HCI
=========================

`Epp et al. (2011) <https://doi.org/10.1145/1978942.1979046>`_ describes keystroke dynamics as ‘the study of the unique timing patterns in an individual's typing, and typically includes extracting keystroke timing features such as the duration of a key press and the time elapsed between key presses”.

Recently, keystroke dynamics have been used in affective computing research to detect user affective states like mood and emotions (Epp et al. 2011; Khanna & Sasikumar, 2010).

Attributes taking into consideration when analuzing keystroke dynamics are: tying speed, mode, std. deviation/variance, range, total time taken, number of backspaces used and interval between typing.

There is not much research in analyzing keystroke dynamics and end-users behavioral states. Some related research may concern personality detection through keyboard and mouse input.

The keyboard attributes measured in two exploratory studies were ‘key-up’ and key-down’. Their findings revealed some limited significance since only recording the standard deviation of the average time between events gave some insight into a user's activity level, a sub trait of extraversion.

In Vizer, Zhou, and Sears (2009) the authors used keystroke timing features of free text in conjunction with linguistic features to identify cognitive and physical stress.
In a more related study of Dijkstra (2013) the author examined the correlation between mouse or keyboard input and self-efficacy levels. Although mouse input showed some promising results for detecting self-efficacy levels, no correlations were found between typing keyboard behavior and self-efficacy.


