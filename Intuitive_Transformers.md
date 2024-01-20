# Intuitive Transformers

Transformers are the backbone of huge advances in AI in recent years. A lot of great stuff has come out making the mechanics of the transformer more digestible for people new to AI, like [this one](https://jalammar.github.io/illustrated-transformer/). That's not the goal of this post. In this post, I want to share with you an *intuition* for how to think about what transformers are doing, so that you can better understand the math (if you choose to), or just be better able to conceptualize the model's inner workings without it.

***Ok I'm interested, how do transformers work?***

For a moment, let's forget about "next word prediction", the task you've heard so much about. Let's imagine a simpler and more abstract setup: one where you have the whole sentence (nothing has been omitted), and you'd like to build a machine learning system that understands what each word "means" in the sentence. There are ways of formalizing variations on this idea, but I'll omit them here and keep it somewhat abstract.

Let's take the following sentence.

> The pitcher of water

An observation: the word "pitcher" can mean different things depending on the sentence. A pitcher can be a pitcher of water or a pitcher in baseball, for example. To build a system that understands what pitcher "means" in this sentence, we need it to *infer what "pitcher" means based on the words around it*. This is the central motivation of the transformer, and is referred to as "contextualization": we want the model to "contextualize" its representation of the word pitcher based on the words around it.

How do we do this? The key idea here is that in the above sentence, the word "water" is very important to understanding the meaning of the word pitcher, but the words "the" and "of" are not. Why? Because you could have something like the following sentence instead (the Yankees are a baseball team)

> The pitcher of the Yankees

***Ok, but how does this connect to LLMs?***

LLMs use this idea in tandem with a simple task that they can run on large amounts of data, that forces the model to learn interesting patterns in that data. That task is "next word prediction". For example,

> The pitcher of water tipped over and spilled.

Would be framed as a question to the LLM:

Question:
> The pitcher of water tipped over and ___

The process is exactly the same as above: the LLM attempts to "contextualize" the blank based on the words around it, and understand the meaning of what's in the blank. We test the LLM based on how well it understood that the blank means "spilled". The idea is that if it can do this well, it probably understands something about our language. This hypothesis has been borne out well, but with some caveats (hallucinations...etc). 

***Ok, I understand the motivation of the transformer architecture and how it connects to the next word prediction task, but how is this actually implemented? What is this "key query value attention" I've heard so much about?***

Ok, so let's go back to our "pitcher of water" example from above. We know that we'd like the word "water" to influence the way our model represents the word "pitcher", and that we don't want "the" and "of" to influence the representation. How do we get this to happen? The attention mechanism is quite simple and elegant. There are two basic steps: getting our model to understand
1. which words matter most in influencing our representation of "pitcher", and
2. how those words should influence the representation

Makes sense, right?

Let's jump into the first step. The intuition here is that we want our model to "see the word pitcher in a certain way" and "see water in a certain way" and see if, looking at them through those lenses, they're similar. To make this more concrete, you can imagine a high level explanation like this: "pitcher is a physical object that relates to other physical objects" and "water is a physical object that relates to other physical objects". If you were to describe "pitcher" and "water" in those ways, by looking at them with those lenses, you would see that they're quite similar. Applying the same lens to the words "the" and "of" might yield explanations like "the is a particle or a conjunction or something pretty abstract and unrelated to physical phenomena". You would see that, by applying this lens to these words, you can see that water is much more relevant to pitcher's representation than "the" or "of".

How does this actually happen? This is where a bit of math comes into play that I'll skim over, but you can get more details in the ["illustrated transformer" article](https://jalammar.github.io/illustrated-transformer/). Basically, the target word ("pitcher") is represented by a vector, the different candidate words ("the", "of", and "water") are represented by vectors, then we learn a *matrix* to transform the representation of the word "pitcher" into a *different representation* and learn another matrix to project the candidate word representations each into different representations. These different representations are intuitively described above ("water is a physical object...etc") and the *matrix* we use to transform the word representations is the "lens" by which we see the word. We call the target word the "query", and the candidates the "keys".

The second part happens with a similar bit of magic: once we have the weights for how important each candidate word is to impacting this query word representation, then we *basically* just take a weighted sum of the candidate representations and add them to the query representation: so the more important words help influence this word's representation more. That's not exactly true, though. In reality, we first pass each of the candidate words through a transformation function as well. We call the output of this process the "values", and the lens that we apply to get them the "value matrix".

All told, in words, what we're doing is "looking at the query word in a certain way (the Query matrix), looking at the key words in a second certain way (the Key matrix), and determining which keys should most influence the query. Then, we're looking at the key words again, this time in a third certain way (the Value matrix), and adding them all together to update the query representation".

There are a couple details I've left out, like positional encoding, but that's the gist of it. If you let me wave my hands a bit about exactly what the transformation matrices are doing and how that connects to "looking at something in a certain way" hopefully this gives some intuition for what the attention mechanism is doing.


