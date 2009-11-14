MIME-Version: 1.0
Received: by 10.216.44.144 with HTTP; Sun, 8 Nov 2009 09:18:05 -0800 (PST)
In-Reply-To: <5f1d9b0c0911080830y1a9f1b92jc0897e9aef88f806@mail.gmail.com>
References: <5f1d9b0c0911080830y1a9f1b92jc0897e9aef88f806@mail.gmail.com>
	 <5f1d9b0c0911080830y1a9f1b92jc0897e9aef88f806@mail.gmail.com>
Date: Sun, 8 Nov 2009 11:18:05 -0600
Delivered-To: sean@allicator.com
Message-ID: <bca0ebe30911080918t6e63067fw5b3ab95f926bddaf@mail.gmail.com>
Subject: Re: noticed a minor thing...
From: Sean Fioritto <sean@allicator.com>
To: postosaurus@postosaurus.com
Content-Type: multipart/alternative; boundary=001485f626b09594cf0477df420b

--001485f626b09594cf0477df420b
Content-Type: text/plain; charset=ISO-8859-1

So I opted to change it. I was just being laz and didn't want to update the
database in prod. However, the link field you had set a limit of 512 and I
needed to set it to a longer length to accomodate longer urls. (IE has a
limit of around 2000 so I set it to that limit). Since I was in there I
changed the field to mlist. Also changing the 'link' field to 'url'.

Also, it seems as if you forgot to add your links.html template to git. If
you get set on github you can do that, but it can also wait until you get
back. Just FYI I'm pretty sure these changes will break your template -- I
can fix it or you can, whoever gets to it first.

- Sean

On Sun, Nov 8, 2009 at 10:30 AM, Sean Fioritto <sean.fioritto@gmail.com>wrote:

> In your Link model, you named one of the fields 'list' which is a reserved
> word in Python. Now in the Link model that word is overridden and we can't
> use it like normal. I've done it a thousand times, but just another thing to
> watch out for. I'm leaving it, I don't think it will hurt anything for now.
>
> Also, emacs usually highlights these words as pink -- which I think you
> would never notice. Might be worth looking into adjusting your syntax
> highlighting. If you google "emacs python mode syntax highlighting" I'm sure
> you'll find something to help.
>
> - Sean
>

--001485f626b09594cf0477df420b
Content-Type: text/html; charset=ISO-8859-1
Content-Transfer-Encoding: quoted-printable

So I opted to change it. I was just being laz and didn&#39;t want to update=
 the database in prod. However, the link field you had set a limit of 512 a=
nd I needed to set it to a longer length to accomodate longer urls. (IE has=
 a limit of around 2000 so I set it to that limit). Since I was in there I =
changed the field to mlist. Also changing the &#39;link&#39; field to &#39;=
url&#39;.<br>
<br>Also, it seems as if you forgot to add your links.html template to git.=
 If you get set on github you can do that, but it can also wait until you g=
et back. Just FYI I&#39;m pretty sure these changes will break your templat=
e -- I can fix it or you can, whoever gets to it first.<br>
<br>- Sean<br><br><div class=3D"gmail_quote">On Sun, Nov 8, 2009 at 10:30 A=
M, Sean Fioritto <span dir=3D"ltr">&lt;<a href=3D"mailto:sean.fioritto@gmai=
l.com">sean.fioritto@gmail.com</a>&gt;</span> wrote:<br><blockquote class=
=3D"gmail_quote" style=3D"border-left: 1px solid rgb(204, 204, 204); margin=
: 0pt 0pt 0pt 0.8ex; padding-left: 1ex;">
In your Link model, you named one of the fields &#39;list&#39; which is a r=
eserved word in Python. Now in the Link model that word is overridden and w=
e can&#39;t use it like normal. I&#39;ve done it a thousand times, but just=
 another thing to watch out for. I&#39;m leaving it, I don&#39;t think it w=
ill hurt anything for now.<br>

<br>Also, emacs usually highlights these words as pink -- which I think you=
 would never notice. Might be worth looking into adjusting your syntax high=
lighting. If you google &quot;emacs python mode syntax highlighting&quot; I=
&#39;m sure you&#39;ll find something to help.<br>
<font color=3D"#888888">
<br>- Sean<br>
</font></blockquote></div><br>

--001485f626b09594cf0477df420b--