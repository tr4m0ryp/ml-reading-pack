"""Phases 5-12: detection, language, generative, multimodal, RL, LLMs, graphs, interpretability."""

from reading_pack.catalog.model import P, Phase

PHASE_5 = Phase(5, "Detection, segmentation & visual explanation",
    "Detection and segmentation build directly on the vision backbones you just read, and "
    "Grad-CAM shows how to inspect what those networks learned.", (
    P(46, "Lin", "Lin et al.", 2014, "Microsoft COCO: Common Objects in Context", arxiv="1405.0312"),
    P(47, "Girshick", "Girshick et al.", 2014,
      "Rich feature hierarchies for accurate object detection and semantic segmentation",
      arxiv="1311.2524"),
    P(48, "Girshick", "Girshick", 2015, "Fast R-CNN", arxiv="1504.08083"),
    P(49, "Ren", "Ren et al.", 2015,
      "Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks",
      arxiv="1506.01497"),
    P(50, "Redmon", "Redmon et al.", 2016, "You Only Look Once: Unified, Real-Time Object Detection",
      arxiv="1506.02640"),
    P(51, "Liu", "Liu et al.", 2016, "SSD: Single Shot MultiBox Detector", arxiv="1512.02325"),
    P(52, "Lin", "Lin et al.", 2017, "Feature Pyramid Networks for Object Detection", arxiv="1612.03144"),
    P(53, "Lin", "Lin et al.", 2017, "Focal Loss for Dense Object Detection", arxiv="1708.02002"),
    P(54, "He", "He et al.", 2017, "Mask R-CNN", arxiv="1703.06870"),
    P(55, "Long", "Long, Shelhamer, Darrell", 2015,
      "Fully Convolutional Networks for Semantic Segmentation", arxiv="1411.4038"),
    P(56, "Ronneberger", "Ronneberger, Fischer, Brox", 2015,
      "U-Net: Convolutional Networks for Biomedical Image Segmentation", arxiv="1505.04597"),
    P(57, "Chen", "Chen et al.", 2017,
      "DeepLab: Semantic Image Segmentation with Deep Convolutional Nets, Atrous Convolution, "
      "and Fully Connected CRFs", arxiv="1606.00915"),
    P(58, "Selvaraju", "Selvaraju et al.", 2017,
      "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization",
      arxiv="1610.02391"),
))

PHASE_6 = Phase(6, "Sequences, language & transformers",
    "Sequence modelling runs from word vectors through recurrent encoder-decoders and attention "
    "to the Transformer, the architecture behind modern NLP.", (
    P(59, "Mikolov", "Mikolov et al.", 2013,
      "Efficient Estimation of Word Representations in Vector Space", arxiv="1301.3781"),
    P(60, "Mikolov", "Mikolov et al.", 2013,
      "Distributed Representations of Words and Phrases and their Compositionality",
      arxiv="1310.4546"),
    P(61, "Pennington", "Pennington, Socher, Manning", 2014,
      "GloVe: Global Vectors for Word Representation", urls=("https://aclanthology.org/D14-1162.pdf",)),
    P(62, "Cho", "Cho et al.", 2014,
      "Learning Phrase Representations using RNN Encoder-Decoder for Statistical Machine Translation",
      arxiv="1406.1078"),
    P(63, "Sutskever", "Sutskever, Vinyals, Le", 2014,
      "Sequence to Sequence Learning with Neural Networks", arxiv="1409.3215"),
    P(64, "Bahdanau", "Bahdanau, Cho, Bengio", 2015,
      "Neural Machine Translation by Jointly Learning to Align and Translate", arxiv="1409.0473"),
    P(65, "Ba", "Ba, Kiros, Hinton", 2016, "Layer Normalization", arxiv="1607.06450"),
    P(66, "Vaswani", "Vaswani et al.", 2017, "Attention Is All You Need", arxiv="1706.03762"),
    P(67, "Loshchilov", "Loshchilov & Hutter", 2019, "Decoupled Weight Decay Regularization",
      arxiv="1711.05101"),
    P(68, "Devlin", "Devlin et al.", 2019,
      "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
      arxiv="1810.04805", urls=("https://aclanthology.org/N19-1423.pdf",)),
    P(69, "Liu", "Liu et al.", 2019, "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
      arxiv="1907.11692"),
    P(70, "Radford", "Radford et al.", 2019, "Language Models are Unsupervised Multitask Learners",
      urls=("https://cdn.openai.com/better-language-models/"
            "language_models_are_unsupervised_multitask_learners.pdf",)),
    P(71, "Raffel", "Raffel et al.", 2020,
      "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer",
      arxiv="1910.10683", urls=("https://www.jmlr.org/papers/volume21/20-074/20-074.pdf",)),
    P(72, "Wolf", "Wolf et al.", 2020, "Transformers: State-of-the-Art Natural Language Processing",
      arxiv="1910.03771", urls=("https://aclanthology.org/2020.emnlp-demos.6.pdf",)),
    P(73, "Brown", "Brown et al.", 2020, "Language Models are Few-Shot Learners", arxiv="2005.14165"),
))

PHASE_7 = Phase(7, "Generative models",
    "Generative models reuse the same networks for the opposite task: learning to produce data "
    "rather than to label it.", (
    P(74, "Kingma", "Kingma & Welling", 2014, "Auto-Encoding Variational Bayes", arxiv="1312.6114"),
    P(75, "Goodfellow", "Goodfellow et al.", 2014, "Generative Adversarial Nets", arxiv="1406.2661"),
    P(76, "Radford", "Radford, Metz, Chintala", 2016,
      "Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks",
      arxiv="1511.06434"),
    P(77, "Isola", "Isola et al.", 2017, "Image-to-Image Translation with Conditional Adversarial Networks",
      arxiv="1611.07004"),
    P(78, "Zhu", "Zhu et al.", 2017,
      "Unpaired Image-to-Image Translation using Cycle-Consistent Adversarial Networks",
      arxiv="1703.10593"),
    P(79, "Karras", "Karras, Laine, Aila", 2019,
      "A Style-Based Generator Architecture for Generative Adversarial Networks", arxiv="1812.04948"),
    P(80, "Ho", "Ho, Jain, Abbeel", 2020, "Denoising Diffusion Probabilistic Models", arxiv="2006.11239"),
))

PHASE_8 = Phase(8, "Transformers in vision & multimodal",
    "Transformers then return to vision and join images with text, merging the threads of "
    "phases 4 to 7.", (
    P(81, "Dosovitskiy", "Dosovitskiy et al.", 2021,
      "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale", arxiv="2010.11929"),
    P(82, "Liu", "Liu et al.", 2021,
      "Swin Transformer: Hierarchical Vision Transformer using Shifted Windows", arxiv="2103.14030"),
    P(83, "Carion", "Carion et al.", 2020, "End-to-End Object Detection with Transformers",
      arxiv="2005.12872"),
    P(84, "Radford", "Radford et al.", 2021,
      "Learning Transferable Visual Models From Natural Language Supervision", arxiv="2103.00020"),
    P(85, "Rombach", "Rombach et al.", 2022,
      "High-Resolution Image Synthesis with Latent Diffusion Models", arxiv="2112.10752"),
    P(86, "Kirillov", "Kirillov et al.", 2023, "Segment Anything", arxiv="2304.02643"),
))

PHASE_9 = Phase(9, "Reinforcement learning & alignment",
    "Reinforcement learning closes the loop from prediction to action, ending with the RLHF "
    "recipe used to align language models.", (
    P(87, "Mnih", "Mnih et al.", 2015, "Human-level control through deep reinforcement learning",
      doi="10.1038/nature14236"),
    P(88, "Silver", "Silver et al.", 2016,
      "Mastering the game of Go with deep neural networks and tree search", doi="10.1038/nature16961"),
    P(89, "Schulman", "Schulman et al.", 2017, "Proximal Policy Optimization Algorithms",
      arxiv="1707.06347"),
    P(90, "Ouyang", "Ouyang et al.", 2022,
      "Training language models to follow instructions with human feedback", arxiv="2203.02155"),
))

PHASE_10 = Phase(10, "Modern LLM practice",
    "Modern LLM practice applies everything so far: open foundation models, cheap fine-tuning, "
    "prompting and retrieval.", (
    P(91, "Touvron", "Touvron et al.", 2023, "LLaMA: Open and Efficient Foundation Language Models",
      arxiv="2302.13971"),
    P(92, "Hu", "Hu et al.", 2022, "LoRA: Low-Rank Adaptation of Large Language Models",
      arxiv="2106.09685"),
    P(93, "Wei", "Wei et al.", 2022,
      "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models", arxiv="2201.11903"),
    P(94, "Lewis", "Lewis et al.", 2020,
      "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", arxiv="2005.11401"),
))

PHASE_11 = Phase(11, "Graphs & scientific ML",
    "Graph networks and AlphaFold show how deep learning extends to relational and scientific "
    "data beyond grids and sequences.", (
    P(95, "Kipf", "Kipf & Welling", 2017,
      "Semi-Supervised Classification with Graph Convolutional Networks", arxiv="1609.02907"),
    P(96, "Hamilton", "Hamilton, Ying, Leskovec", 2017, "Inductive Representation Learning on Large Graphs",
      arxiv="1706.02216"),
    P(97, "Velickovic", "Veličković et al.", 2018, "Graph Attention Networks", arxiv="1710.10903"),
    P(98, "Jumper", "Jumper et al.", 2021, "Highly accurate protein structure prediction with AlphaFold",
      urls=("https://www.nature.com/articles/s41586-021-03819-2.pdf",),
      doi="10.1038/s41586-021-03819-2"),
))

PHASE_12 = Phase(12, "Interpretability",
    "Interpretability comes last, because explaining a model's predictions only means something "
    "once you understand the models themselves.", (
    P(99, "Ribeiro", "Ribeiro, Singh, Guestrin", 2016,
      "\"Why Should I Trust You?\": Explaining the Predictions of Any Classifier", arxiv="1602.04938"),
    P(100, "Lundberg", "Lundberg & Lee", 2017, "A Unified Approach to Interpreting Model Predictions",
      arxiv="1705.07874"),
))
