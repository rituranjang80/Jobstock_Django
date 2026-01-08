'use client'

import React from 'react'
import Link from 'next/link';

import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay,EffectFade} from 'swiper/modules';
import 'swiper/css';

import { jobData } from '../data/data'

import CtaOne from '../components/cta/cta-one'
import ClientOne from '../components/client/client-one'
import PricingTwo from '../components/pricing/pricing-two'
import SubscribeOne from '../components/subscribe/subscribe-one'
import ScrollToTop from '../components/scroll-to-top'
import FooterLight from '../components/footer/footer-light'
import NavBgWhite from '../components/navbar/nav-bg-white'
import CategoryTwo from '../components/category/category-two'
import FeatureJob from '../components/job/feature-job'
import NavTop from '../components/navbar/nav-top'

interface JobData{
    id: number;
    image: string;
    name: string;
    tag: string[];
    jobtype: string;
    title: string;
    skills: string;
    value: string;
    open: string;
    location: string;
    name2: string;
    rate: string[];
    review: string;
}

export default function SliderHome() {
  return (
    <>
        <NavTop/>

        <NavBgWhite/>  

        <div className="slider-home">
            <Swiper className="slider-banner" modules={[Autoplay,EffectFade]} loop={true}  autoplay={{ delay: 2000, disableOnInteraction: false, }} effect={'fade'} speed={300}>
                <SwiperSlide className="bg-cover d-flex align-items-center" style={{backgroundImage:`url('/img/slide-banner-1.jpg')`, minHeight:'540px'}} data-overlay="5">
                    <div className="container">
                        <div className="row justify-content-center">
                            <div className="col-xxl-12 col-xl-12 col-lg-12 col-12">
                                <div className="slider-caption">
                                    <h1 className="text-light">Real Jobs, Real People, Real Success</h1>
                                    <p className="fs-5 text-light">The toppings you may chose for that TV dinner pizza slice when you forgot to shop for foods</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </SwiperSlide>
                
                <SwiperSlide className="bg-cover d-flex align-items-center" style={{backgroundImage:`url('/img/slide-banner-3.jpg')`, minHeight:'540px'}} data-overlay="5">
                    <div className="container">
                        <div className="row justify-content-center">
                            <div className="col-xxl-12 col-xl-12 col-lg-12 col-12">
                                <div className="slider-caption">
                                    <h1 className="text-light">Discover Jobs. Take Action. Win Big.</h1>
                                    <p className="fs-5 text-light">The toppings you may chose for that TV dinner pizza slice when you forgot to shop for foods</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </SwiperSlide>
                
                <SwiperSlide className="bg-cover d-flex align-items-center" style={{backgroundImage:`url('/img/slide-banner-4.jpg')`, minHeight:'540px'}} data-overlay="5">
                    <div className="container">
                        <div className="row justify-content-center">
                            <div className="col-xxl-12 col-xl-12 col-lg-12 col-12">
                                <div className="slider-caption">
                                    <h1 className="text-light">Find Work. Build Skills. Grow Fast.</h1>
                                    <p className="fs-5 text-light">The toppings you may chose for that TV dinner pizza slice when you forgot to shop for foods</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </SwiperSlide>
                
                <SwiperSlide className="bg-cover d-flex align-items-center" style={{backgroundImage:`url('/img/slide-banner-2.jpg')`, minHeight:'540px'}} data-overlay="5">
                    <div className="container">
                        <div className="row justify-content-center">
                            <div className="col-xxl-12 col-xl-12 col-lg-12 col-12">
                                <div className="slider-caption">
                                    <h1 className="text-light">One Click Closer to Your Next Big Opportunity</h1>
                                    <p className="fs-5 text-light">The toppings you may chose for that TV dinner pizza slice when you forgot to shop for foods</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </SwiperSlide>
                
            </Swiper>
        </div> 

        <section className="py-0">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xxl-9 col-xl-10 col-lg-12 col-md-12">
                        <div className="card rounded-4 shadow-sm w-100 px-4 px-xl-5 py-5 ovr-top">
                            
                            <form className="slider-search-form mb-4">
                                <div className="inner-form-block rounded-pill border p-2">
                                    <div className="d-flex align-items-center justify-content-between gap-2 w-100">
                                        <div className="form-group flex-fill m-0">
                                            <div className="input-with-icon">
                                                <input type="text" className="form-control fs-6 bg-transparent" id="trendingSearch" placeholder="Skills, Designations, Keyword"/>
                                                <i className="bi bi-search text-main fs-5"></i>
                                            </div>
                                        </div>
                                        <div className="submit-block"><button type="submit" className="square--60 btn-main border-0 fs-5 circle"><i className="bi bi-search"></i></button></div>
                                    </div>
                                </div>
                            </form>
                            
                            <div id="tagContainer">
                                <ul className="p-0 m-0 d-flex align-items-center justify-content-center gap-2 flex-wrap">
                                    <li><span className="badge badge-md badge-maintag rounded-pill">Web Designer</span></li>
                                    <li><span className="badge badge-md badge-maintag rounded-pill">Front-end Developer</span></li>
                                    <li><span className="badge badge-md badge-maintag rounded-pill">Figma Developer</span></li>
                                    <li><span className="badge badge-md badge-maintag rounded-pill">UI/UX Designer</span></li>
                                </ul>
                            </div>

                        </div>
                    </div>
                </div>
            </div>
        </section>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Featured Jobs</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <FeatureJob/>
            </div>
        </section>

        <section className="gray-simple">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Explore Top Categories</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <CategoryTwo border={false}/>
            </div>
        </section>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Trending jobs Jobs</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                
                <div className="row justify-content-center gx-3 gy-4 mb-5">
                    {jobData.slice(0,5).map((item:JobData,index:number)=>( 
                        <div className="col-xxl-10 col-xl-12 col-lg-12 col-md-12" key={index}>
                            <div className="jbs-list-box border">
                                <div className="jbs-list-head">
                                    <div className="jbs-list-head-thunner">
                                        <div className="jbs-list-emp-thumb jbs-verified"><Link href="/job-detail"><figure><img src={item.image} className="img-fluid" alt=""/></figure></Link></div>
                                        <div className="jbs-list-job-caption">
                                            <div className="jbs-job-types-wrap"><span className="label text-green bg-light-green">{item.jobtype}</span></div>
                                            <div className="jbs-job-title-wrap"><h4><Link href="/job-detail" className="jbs-job-title">{item.title}</Link></h4></div>
                                            <div className="jbs-job-mrch-lists">
                                                <div className="single-mrch-lists">
                                                    <span>{item.name}</span>.<span><i className="fa-solid fa-location-dot me-1"></i>{item.location}</span>.<span>07 Apr 2023</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="jbs-list-head-middle">
                                        <div className="elsocrio-jbs"><div className="ilop-tr"><i className="fa-solid fa-sack-dollar"></i></div><h5 className="jbs-list-pack">{item.value}<span className="patype">\PA</span></h5></div>
                                    </div>
                                    <div className="jbs-list-head-last">
                                        <Link href="/job-detail" className="btn btn-md btn-gray px-3 me-2">View Detail</Link>
                                        <Link href="#" className="btn btn-md btn-main px-3">Quick Apply</Link>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
                
                <div className="row">
                    <div className="col-lg-12 col-md-12 col-sm-12">
                        <div className="d-flex align-items-center justify-content-center">
                            <Link href="#" className="btn btn-dark px-5 rounded-pill">Explore More Jobs</Link>
                        </div>
                    </div>
                </div>
                
            </div>
        </section>
        <div className="clearfix"></div>

        <CtaOne/>

        <section className="gray">
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

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Explore our Prices</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <PricingTwo/>
            </div>	
        </section>

        <SubscribeOne/>
        <FooterLight/>

        <ScrollToTop/>
    </>
  )
}
