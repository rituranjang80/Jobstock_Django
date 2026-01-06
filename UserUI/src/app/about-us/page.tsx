import React from 'react'
import Image from 'next/image'

import NavBgWhite from '../components/navbar/nav-bg-white'
import ProcessTwo from '../components/process/process-two'
import ClientOne from '../components/client/client-one'
import FooterTopTwo from '../components/footer/footer-top-two'
import FooterLightTwo from '../components/footer/footer-light-two'
import ScrollToTop from '../components/scroll-to-top'

import { teamTwo } from '../data/data'

interface TeamData{
    image: string;
    name: string;
    position: string;
}

export default function AboutUs() {
  return (
    <>
        <NavBgWhite/>

        <section className="page-head bg-cover" style={{backgroundColor:'#017efa', backgroundImage:`url('/img/about.jpg')`, backgroundRepeat:'no-repeat'}} data-overlay="4">
            <div className="container">
                <div className="row">
                    <div className="col-xl-8 col-lg-9 col-md-12">
                        <h1 className="text-white mb-4">Who We are<br/> & Our Smart Mission</h1>
                        <p className="text-white mb-4">At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. </p>
                        <button type="button" className="btn btn-main fw-medium">Get In Touch</button>
                    </div>
                </div>
            </div>
        </section>

        <section>
            <div className="container">
                <div className="row align-items-center justify-content-between">
                    <div className="col-lg-6 col-md-6">
                        <div className="story-wrap explore-content">
                            <h2>Our Mission & Story</h2>
                            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                            <p className="fw-light mb-4">At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia deserunt mollitia animi, id est laborum et dolorum fuga. Et harum quidem rerum facilis est et expedita distinctio. </p>
                            <button type="button" className="btn fw-medium btn-main">Start Today Now</button>
                        </div>
                    </div>
                    <div className="col-lg-5 col-md-6">
                        <Image src='/img/bn-1.png' width={0} height={0} sizes='100vw' style={{width:'100%', height:'auto'}} className="img-fluid" alt=""/>
                    </div>
                </div>
            </div>
        </section>

        <section className="bg-light">
            <div className="container">
                <div className="row">
                    <div className="col-lg-12 col-md-12">
                        <div className="sec-heading center">
                            <h2>Meet Our Team</h2>
                            <p>Professional & Dedicated Team</p>
                        </div>
                    </div>
                </div>
                <div className="row gx-3 gy-4">
                    {teamTwo.map((item:TeamData,index:number)=>( 
                        <div className="col-xl-3 col-lg-4 col-md-4 col-sm-6" key={index}>
                            <div className="team-grid">
                                <div className="teamgrid-user">
                                    <Image src={item.image} width={0} height={0} sizes='100vw' style={{width:'100%', height:'auto'}} alt="" className="img-fluid" />
                                </div>
                                <div className="teamgrid-content">
                                    <h4>{item.name}</h4>
                                    <span className="text-main">{item.position}</span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>

        <ProcessTwo/>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Good Reviews By Customers</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <ClientOne/>
            </div>	
        </section>

        <FooterTopTwo/>

        <FooterLightTwo/>

        <ScrollToTop/>
    </>
  )
}
