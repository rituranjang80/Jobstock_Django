import React from 'react'
import NavBgWhite from '../components/navbar/nav-bg-white'
import PartnerTwo from '../components/partner/partner-two'
import FeatureJobTwo from '../components/job/feature-job-two'
import AboutOne from '../components/about/about-one'
import CategoryOne from '../components/category/category-one'
import ProcessTwo from '../components/process/process-two'
import ExploreJob from '../components/job/explore-job'
import CandidateOne from '../components/candidate/candidate-one'
import PricingOne from '../components/pricing/pricing-one'
import SubscribeTwo from '../components/subscribe/subscribe-two'
import FooterLight from '../components/footer/footer-light'
import ScrollToTop from '../components/scroll-to-top'
import Image from 'next/image'

export default function HomeTwo() {
  return (
    <>
        <NavBgWhite/>   

        <div className="image-bg hero-header p-150" style={{backgroundImage:`url('/img/simple-banner.jpg')`, backgroundRepeat:'no-repeat'}}>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-lg-9 col-md-11 col-sm-12">
                        <div className="inner-banner-text text-center">
                            <div className="inner-banner-eclips mb-2"><span className="label p-2 px-4 rounded-5 fw-medium text-light bg-main">Get Your Hot Jobs</span></div>
                            <h1>Find the great jobs<br/>offer for you</h1>
                            <p className="fs-5">Getting a new job is never easy. Check what new jobs we have in store for you on JobStock.</p>
                        </div>
                        <div className="search-from-clasic mt-5">
                            <div className="hero-search-content">
                                <div className="row">
                                    <div className="col-xl-10 col-lg-10 col-md-9 col-sm-12">
                                        <div className="classic-search-box">
                                            <div className="form-group full">
                                                <div className="input-with-icon">
                                                    <input type="text" className="form-control" placeholder="Search for locality, landmark, project, or builder"/>
                                                    <Image src='/img/pin.svg' height={20} width={20} alt=""/>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="col-xl-2 col-lg-2 col-md-3 col-sm-12">
                                        <div className="form-group">
                                            <button type="submit" className="btn btn-main full-width">Search</button>
                                        </div>
                                    </div>
                                            
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <PartnerTwo/>
        <div className="clearfix"></div>

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
                <FeatureJobTwo/>
            </div>
        </section>

        <div className="position-relative">
            <AboutOne/>
        </div>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-lg-8 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Explore Top Categories</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <CategoryOne light={true}/>
            </div>
        </section>

        <ProcessTwo/>

        <section>
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Explore Job in NewYork</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <ExploreJob/>
            </div>		
        </section>

        <section className="gray-simple">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-6 col-lg-7 col-md-10 text-center">
                        <div className="sec-heading center">
                            <h2>Hire Talents & Experts</h2>
                            <p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores</p>
                        </div>
                    </div>
                </div>
                <CandidateOne border={false}/>
            </div>		
        </section>

        <section>
            <PricingOne/>
        </section>

        <SubscribeTwo/>

        <FooterLight/>

        <ScrollToTop/>

    </>
  )
}

