import React from 'react'

import NavBgWhite from '../components/navbar/nav-bg-white'
import FooterTopTwo from '../components/footer/footer-top-two'
import FooterLightTwo from '../components/footer/footer-light-two'
import ScrollToTop from '../components/scroll-to-top'

import { contact } from '../data/data'

interface Contact{
    icon: string;
    title: string;
    desc: string;
    desc2: string;
}

export default function Contact() {
  return (
    <>
        <NavBgWhite/>

        <section className="bg-cover bg-second" style={{backgroundImage:`url('/img/bg2.png')`, backgroundRepeat:'no-repeat'}}>
            <div className="container">
                <div className="row">
                    <div className="col-lg-12 col-md-12">
                        <h2 className="ipt-title text-light">Get In touch</h2>
                        <span className="text-light opacity-75">Get all latest news and updates</span>
                    </div>
                </div>
            </div>
        </section>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <label className="label text-success bg-light-success">Grow Your Business</label>
                            <h2>Activate Next Now</h2>
                            <p>Please fill the form and we will guide you to the best solution. Our experts will get in touch soon.</p>
                        </div>
                    </div>
                </div>
            
                <div className="row align-items-center justify-content-center">
                    <div className="col-lg-10 col-md-12">
                        <div className="row">
                            <div className="col-lg-6 col-md-6">
                                <div className="form-group">
                                    <label>Name</label>
                                    <input type="text" className="form-control simple"/>
                                </div>
                            </div>
                            <div className="col-lg-6 col-md-6">
                                <div className="form-group">
                                    <label>Email</label>
                                    <input type="email" className="form-control simple"/>
                                </div>
                            </div>
                            <div className="col-lg-6 col-md-6">
                                <div className="form-group">
                                    <label>Subject</label>
                                    <input type="text" className="form-control simple"/>
                                </div>
                            </div>
                            <div className="col-lg-6 col-md-6">
                                <div className="form-group">
                                    <label>Phone.</label>
                                    <input type="text" className="form-control simple"/>
                                </div>
                            </div>
                            <div className="col-lg-12 col-md-12">
                                <div className="form-group">
                                    <label>Message</label>
                                    <textarea className="form-control simple"></textarea>
                                </div>
                            </div>
                            <div className="col-lg-12 col-md-12">
                                <div className="form-group">
                                    <button className="btn btn-main px-5" type="submit">Submit Request</button>
                                </div>
                            </div>
                        </div>				
                    </div>		
                </div>

                <div className="row align-items-center justify-content-center mt-5">
                    <div className="col-lg-10 col-md-12">
                        <div className="ctr-jobstock-box">
                            {contact.map((item:Contact,index:number)=>( 
                                <div className="ctr-jobstock-signl" key={index}>
                                    <div className="ctr-jobstock-signl-ico"><i className={item.icon}></i></div>
                                    <div className="ctr-jobstock-signl-caption">
                                        <h5>{item.title}</h5>
                                        <p>{item.desc}</p>
                                        <p>{item.desc2}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <FooterTopTwo/>

        <FooterLightTwo/>

        <ScrollToTop/>
    </>
  )
}
