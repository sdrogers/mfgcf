{% load staticfiles %}

## Table of Contents

1. <a href="#getting_started">Getting Started</a>
2. <a href="#prerequisites">Prerequisites</a>

---

#### <a name="getting_started">1. Getting Started</a>

To log in to Ms2lda.org, go to the <a href="http://ms2lda.org/registration/login/" target="_blank" title="Ms2lda">Login</a> page.

Once there, please input your username and password. If you have not been provided with a username and password, 
please email us to create an account. Once you hit enter, or click 'Submit', you should find yourself in your 
main page listing all the experiments that you have access to (whether in edit or read-only modes). 

There are two experiment types that can be created on Ms2lda.org:

- LDA experiments have Mass2Motifs (patterns of co-occuring fragment and neutral loss features) 
that potentially indicate structural families to be discovered in a completely unsupervised manner from the data using LDA

- Decomposition experiments used pre-defined Mass2Motifs that could be annotated from another experiment
in your data.

---

#### <a name="prerequisites">2. Prerequisites</a>

To analyse your data in Ms2lda.org, you first need:

1. Your fragmentation data in mzML, MSP or MGF formats
2. A list of MS1 peaks (optional). When fragmentation data in mzML format is provided, this list will be used to seed the MS1 peaks during
feature extraction so only peaks that match the MS1 list within certain m/z and RT tolerances will be used.

Once you have these available, from the Experiment screen, click on the **Create Experiment** button, shown in <strong><font color="red">(A)</font></strong> below. 
A screen will appear asking you to upload your data and define the parameters for feature extraction and inference (see Section 4 for more details).
Upon clicking submit, the experiment will be processed in a job queue. While processing, it is also shown in the list of **Pending Experiments**, shown in <strong><font color="red">(B)</font></strong> below. 
Upon completion, experiments are moved to the list of LDA or Decomposition experiments, depending on the experiment type that you have specified.

<!-- ![Create Experiment][create_experiment] -->
<p class="centered">
<img src="{% static 'images/user_guide/create_experiment.png' %}" class="img-thumbnail" alt="Create Experiment" width="100%" style="float:none;margin:auto;">
</p>

---