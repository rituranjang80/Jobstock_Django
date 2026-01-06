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

export default function ProcessThree() {
  return (
        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Steps Our Working Process</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                
                <div className="row align-items-center gx-4 gy-4">
                    {data.map((item:Data,index:number)=>( 
                        <div className="col-xl-4 col-lg-4 col-md-12 col-sm-12" key={index}>
                            <div className="jobstock-posted-box-y78">
                                <div className="jobstock-posted-body-y78">
                                    <div className="serv-ctr-title"><h2 className="text-main">{item.no}</h2></div>
                                    <div className="serv-ctr-subtitle"><h5>{item.title}</h5></div>
                                    <div className="serv-ctr-decs"><p>{item.desc}</p></div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
  )
}
