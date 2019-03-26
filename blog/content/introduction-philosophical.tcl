set date "2019-03-26"
set title "An Introduction to bigCGI Part 1: Philosophical"
set tags [list meta bigcgi]
set content "
<p>
In this first post of the bigCGI blog, I'd like to answer 
the \"why\" of bigCGI.  In future posts, I'll be addressing
the \"who\" and the \"how\" of this project, but I believe 
one of the most important aspects of bigCGI is it's 
existence itself.
</p>

<p>
I like to think of bigCGI as an art constructed of software.
Just like physical art, it can be functional, but it's 
primary purpose is an expression of the views of it's 
creator.  bigCGi is a platform that is a reaction to 
trends, bloat, and corporate influnece of the internet.  It
serves as a testament to the power of open standards,
tech minimalism, and a cooperative internet. 
</p>

<h5>Tech Minimalism</h5>
<p>
In his book <i>Nine Chains to the Moon</i>,
 R. Buckminster Fuller explored the concept he coined as 
ephemeralism, defined simply as \"doing more with less\".
This notion is largely ignored by the technology community,
where trends reign supreme and increased levels of 
abstraction are preferred to refinement of current 
implementations.
</p>
<p>
CGI is the simplest way to create dynamic web content.
It is a simple standard that can be implemented by nearly
every programming language, without the need for even a 
library.  Any language that can read environment 
variables and standard in, and write to standard out, is 
able to use CGI.  Simplicity brings democratization of the
web to all technologies, not just the trendy ones.
</p>
<p>
CGI lends itself to stateless application development, and
because each web request is mapped to a script, encourages
small modules that follow the single responsibility 
principle.  In many ways, the minimalistic nature of the
standard manifests itself in many ways downstream.
</p>
<p>
When CGI was deemed to slow for modern applications, 
fast-cgi, server modules, and eventually application servers
largely replaced it for serving web applications.  The 
rise of serverless, however, where many of the use cases
are for background tasks, and cold starts are accepted as normal, seems like area for tech minimalism to thrive.
</p>
<h5>Open Standards and the Cooperative Internet</h5>
  

"