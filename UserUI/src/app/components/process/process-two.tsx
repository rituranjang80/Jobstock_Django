import React from 'react'

let data = [
    {
        no:'01.',
        title:'Create An Account',
        desc:`Post A Job To Tell Us About Your Project. We'll Quickly Match You With The Right Freelancers Find Place Best. Nor again is there anyone who loves.`
    },
    {
        no:'02.',
        title:'Search Jobs',
        desc:`Post A Job To Tell Us About Your Project. We'll Quickly Match You With The Right Freelancers Find Place Best. Nor again is there anyone who loves.`
    },
    {
        no:'03.',
        title:'Save & Apply Jobs',
        desc:`Post A Job To Tell Us About Your Project. We'll Quickly Match You With The Right Freelancers Find Place Best. Nor again is there anyone who loves.`
    },
]

interface Data{
    no: string;
    title: string;
    desc: string;
}

export default function ProcessTwo() {
  return (
    <section className="bg-second">
        <div className="container">
            <div className="row justify-content-center">
                <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                    <div className="sec-heading center light">
                        <h2>Choose What You Need</h2>
                        <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                    </div>
                </div>
            </div>
            
            <div className="row align-items-center gx-4 gy-4">
                {data.map((item:Data,index:number)=>( 
                    <div className="col-xl-4 col-lg-4 col-md-12 col-sm-12" key={index}>
                        <div className="jobstock-posted-box-y78 colored">
                            <div className="jobstock-posted-body-y78">
                                <div className="serv-ctr-title"><h2 className="text-green">{item.no}</h2></div>
                                <div className="serv-ctr-subtitle"><h5 className="text-light">{item.title}</h5></div>
                                <div className="serv-ctr-decs"><p className="text-light opacity-75">{item.desc}</p></div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    </section>
  )
}
