set date "2019-10-10"
set title "Hello World: An Introduction to bigCGI"
set tags [list meta bigcgi]
set content "<h2>Hello world!</h2>
<p>In this first post of the bigCGI blog, I'd like to give a brief overview about
this project, especially concerning my  motivations and goals for bigCGI.  I've been meaning 
to write this post for a while, but always get bogged down by various insecurities, so I'm going
to keep it informal and loose but also (hopefully) coherent. 
</p>
<h2>Me</h2>
<p>I'm Brian, a sysadmin and musician from Cincinnati.  My Github username is bmsauer, and that's
where I currently host the source of bigCGI.  It's also my bigCGI username, if you happen to come
across one of my apps.  I'm the only developer of bigCGI, which I have been sporadically working on
for the past couple of years.  It initially started out as a joke with my coworkers, but as I began
building it I realized there are some interesting properties about CGI.  At one point I thought it
could be a business, but now I'm not very concerned with that.  Now, I want it to stand as a piece
of \"software art\", meaning it's existence is an expression of what I believe about
software craftsmanship.  In order for this statement to be strong, it also has to be useful, which
it is to the point where any web application I want to make I try to do in bigCGI.
</p>
<h2>What is bigCGI</h2>
<p>
bigCGI is a function as a service (FaaS) platform that uses CGI as the function definition.  CGI
is just an old web standard that presented a format so that web pages could send inputs to a program
and receive outputs, paving the way for dynamic web pages that respond to user input.  CGI fell out
of favor for FastCGI, server specific API's, and other protocols like WSGI.  It is primarily only
used in legacy applications.
</p>
<p>
A few years ago, there was a lot of hype around \"serverless\" architectures, which were small
code snippets that would run on demand and scale automatically, invisibly from the developer.  These
services were intended to run background tasks or respond to inconsistent \"bursty\" events, 
offloading unpredictable spikes of processing power to another server.  To me, a small, ephemeral, 
stateless function with well defined inputs and outputs sounded a lot like CGI, so I went ahead and
built bigCGI.
</p>
<p>
On a more technical level, bigCGI is basically a bunch of servers running the bigCGI application that
does two things: implements the CGI standard for calling CGI programs, and manages those servers to
ensure that when a user adds an application, it is propagated to all of the other servers.  For this,
I use MongoDB and a Celery queue to manage the cluster state.  These identical bigCGI servers then 
have their traffic managed by a reverse proxy.
</p> 
<p>
CGI has some interesting properties that make it useful for this application:
<ul>
<li>Easy to program functions, with a well defined standard.</li>
<li>Functions can be any programming language, provided it can read standard in, read environment variables,
 and write to standard out and standard err.</li>
<li>Functions can be run locally or in any webserver that supports CGI, which is nice for testing.</li>
<li>Functions run in process isolation, and can not \"go down\" like a long running process.</li>
<li>CGI functions don't have the cold start problem like containers do.</li>
</ul>
The primary reason why CGI fell out of favor was speed due to the bottle neck of process creation
overhead.  Assuming this bottleneck has not been improved with modern operating systems (still looking
into this), I have two responses to the speed problem: First, for the type of application you should 
be using FaaS for, a few milliseconds of lost time (that is not visible to the end user anyway) is not that important. 
 Second, if a few milliseconds is vitally important to and application, bigCGI just 
isn't the right fit, and that's totally OK, because there are a lot of FaaS options and a lot of other
applications that don't have those requirements.
</p>
<h2>Why bigCGI?</h2>
<p>
bigCGI is something I enjoy working on because it encompasses many different aspects of software
development, both technically and philosophically.  Technically, it has both application development
and infrastructure management components, so I get to do a little of everything.  Philosophically,
it allows me to express some of my ideas concerning how we build, use, and share technology.
</p>
<h3>Tech Minimalism</h3>
<p>
The primary motivation for bigCGI is exploring the concept of tech minimalism in regards to 
development, instead of consumer usage.  Like all minimalistic idealogy, I'm trying to remove as
as much complexity as possible to uncover the purest form of software that is both useful and
sustainable. I'm not sure if minimalism is appropriate for something like FaaS, so I consider 
bigCGI an experiment to see where the limits of minimalism are.  
</p>
<p>
bigCGI demonstrates minimalism in many ways.  First, it uses the CGI standard that itself is
minimal.  It uses common elements in programming (environment variables, standard in/out/er) in
an easy to understand way.  Being an open standard, it has widespread adoption among server
technologies but is easy enough to understand that an implementation is trivial to create. I
had to do exactly that when Apache no longer served bigCGI's needs.
</p>
<p>
Second, bigCGI encourages small stateless apps.  CGI's limited specification, although flexible,
is a constraint that drives CGI apps to typically be this way.  Constraints are good and 
foster innovation, which is ultimately the purpose of minimalism.  I'm actively exploring
this positive feedback loop.
</p>
<p>
Third, bigCGI as a project is built with the idea that one person can manage it.  It uses
a monorepo, runs on bare metal, uses common and well established technology, uses no javascript,
 and is open source. It is easily to manage and modify, and I prioritize working on ways to 
better test and deploy the servers over adding new features.
</p>
<h3>Why Tech Minimalism</h3>
<p>I think minimalism will be important for the field of software development for a few reasons.
The world, in general, needs more sustainability, and our software should reflect that.  For
environmental purposes, our applications should use at little resources as possible so that
they can be powered by renewable resources and run on older recycled hardware.  For our sanity,
we need to stop chasing \"new and convenient\" and focus on \"useful and maintainable\".  
For our creativity, we need constraints but also the ability to look into and understand our
stacks.
</p>
<p>
bigCGI may seem silly to a lot of people, but to me its a challenge to push the limits of
how much we can do with less.
</p>
<h2>Conclusion</h2>
<p>Thank you for reading this post, I hope it makes sense what I'm trying to do here and 
why I think it is important.  If you would like to chat, please send me an email at
bigcgi.app@gmail.com.  You can also check out the project on github, 
at <a href='https://github.com/bmsauer/bigcgi'>https://github.com/bmsauer/bigcgi</a>.
</p>"


