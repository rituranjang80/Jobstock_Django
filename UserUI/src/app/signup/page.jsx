import React from 'react'
import Link from 'next/link'
import NavBgWhite from '../components/navbar/nav-bg-white'
import FooterTopTwo from '../components/footer/footer-top-two'
import FooterLightTwo from '../components/footer/footer-light-two'
import ScrollToTop from '../components/scroll-to-top'
import Image from 'next/image'

export default function Signup() {
  return (
    <>
        <NavBgWhite/>

        <section className="gray-simple ">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-xl-7 col-lg-8 col-md-12">
                        <div className="card rounded-4">
                            <div className="card-body p-4">
                                <form className="p-md-4">
                                    <div className="form-heads d-block mb-4">
                                        <div className="d-flex align-items-center justify-content-start gap-3">
                                            <div className="head-caps">
                                                <h4>Create your Reetch profile</h4>
                                                <p>Search & apply to jobs from India's No.1 Job Site</p>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="form-float d-flex flex-column gap-4">
                                        <div className="form-group mb-0">
                                            <label className="fw-medium fs-6 text-dark">Full Name</label>
                                            <input type="text" className="form-control" placeholder="What is your name?"/>
                                        </div>
                                        <div className="form-group mb-0">
                                            <label className="fw-medium fs-6 text-dark">Email ID<i className="text-danger text-md">*</i></label>
                                            <input type="email" className="form-control" placeholder="Tell us your Email ID"/>
                                            <span className="text-sm opacity-75">We'll send relevant jobs and updates to this email</span>
                                        </div>
                                        
                                        <div className="form-group mb-0">
                                            <label className="fw-medium fs-6 text-dark">Password<i className="text-danger text-md">*</i></label>
                                            <input type="email" className="form-control" placeholder="(Minimum 8 characters)"/>
                                            <span className="text-sm opacity-75">This helps your account stay protected</span>
                                        </div>
                                        
                                        <div className="form-group mb-0">
                                            <label className="fw-medium fs-6 text-dark">Mobile number<i className="text-danger text-md">*</i></label>
                                            <input type="email" className="form-control" placeholder="Enter your mobile number"/>
                                            <span className="text-sm opacity-75">This helps your account stay protected</span>
                                        </div>
                                        
                                        <div className="form-group mb-0">
                                            <label className="fw-medium fs-6 text-dark">Work status<i className="text-danger text-md">*</i></label>
                                            <div className="row g-4">
                                            
                                                <div className="col-sm-6">
                                                    <div className="sing-btn-groups">
                                                        <input type="radio" className="btn-check" name="lokingfor" id="findjob"/>
                                                        <label className="btn btn-md btn-outline-gray h-auto" htmlFor="findjob">
                                                            <div className="d-flex align-items-center gap-3">
                                                                <div className="icons">
                                                                    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                                        <path opacity="0.3" d="M20 15H4C2.9 15 2 14.1 2 13V7C2 6.4 2.4 6 3 6H21C21.6 6 22 6.4 22 7V13C22 14.1 21.1 15 20 15ZM13 12H11C10.5 12 10 12.4 10 13V16C10 16.5 10.4 17 11 17H13C13.6 17 14 16.6 14 16V13C14 12.4 13.6 12 13 12Z" fill="#0b8260"/>
                                                                        <path d="M14 6V5H10V6H8V5C8 3.9 8.9 3 10 3H14C15.1 3 16 3.9 16 5V6H14ZM20 15H14V16C14 16.6 13.5 17 13 17H11C10.5 17 10 16.6 10 16V15H4C3.6 15 3.3 14.9 3 14.7V18C3 19.1 3.9 20 5 20H19C20.1 20 21 19.1 21 18V14.7C20.7 14.9 20.4 15 20 15Z" fill="#0b8260"/>
                                                                    </svg>
                                                                </div>
                                                                <div className="btn-caps text-start">
                                                                    <h6 className="mb-0 lh-base">I'am looking job</h6>
                                                                    <p className="m-0 text-md text-muted">Looking great opportunity for my career</p>
                                                                </div>
                                                            </div>
                                                        </label>
                                                    </div>
                                                </div>
                                                
                                                <div className="col-sm-6">
                                                    <div className="sing-btn-groups">
                                                        <input type="radio" className="btn-check" name="lokingfor" id="findtalent"/>
                                                        <label className="btn btn-md btn-outline-gray h-auto" htmlFor="findtalent">
                                                            <div className="d-flex align-items-center gap-3">
                                                                <div className="icons">
                                                                    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                                        <path opacity="0.3" d="M22 12C22 17.5 17.5 22 12 22C6.5 22 2 17.5 2 12C2 6.5 6.5 2 12 2C17.5 2 22 6.5 22 12ZM12 7C10.3 7 9 8.3 9 10C9 11.7 10.3 13 12 13C13.7 13 15 11.7 15 10C15 8.3 13.7 7 12 7Z" fill="#0b8260"/>
                                                                        <path d="M12 22C14.6 22 17 21 18.7 19.4C17.9 16.9 15.2 15 12 15C8.8 15 6.09999 16.9 5.29999 19.4C6.99999 21 9.4 22 12 22Z" fill="#0b8260"/>
                                                                    </svg>
                                                                </div>
                                                                <div className="btn-caps text-start">
                                                                    <h6 className="mb-0 lh-base">I'am looking job</h6>
                                                                    <p className="m-0 text-md text-muted">Looking great opportunity for my career</p>
                                                                </div>
                                                            </div>
                                                        </label>
                                                    </div>
                                                </div>
                                                
                                            </div>
                                        </div>
                                        
                                        <div className="form-group mb-0">
                                            <div className="form-check form-check-inline">
                                                <input className="form-check-input" type="checkbox" id="promotions" value="option1"/>
                                                <label className="form-check-label" htmlFor="promotions">Send me important updates & promotions via SMS & email</label>
                                            </div>
                                        </div>
                                        
                                        <div className="form-group mb-0">
                                            <p className="confirmTex">By clicking Register, you agree to the<Link href="#" className="text-main"> Terms and Conditions </Link> &amp;<Link href="#" className="text-main"> Privacy Policy </Link> of Jobstock.com</p>
                                            <button type="button" className="btn btn-main full-width">Register now</button>
                                        </div>
                                    </div>
                                </form>

                                <div className="devider position-relative d-block">
                                    <hr className="mb-5 mt-4"/>
                                    <div className="position-absolute top-50 start-50 translate-middle"><span className="square--30 circle bg-white text-muted">OR</span></div>
                                </div>
                                
                                <div className="social-signup d-flex flex-column gap-3 mb-4">
                                    <Link href="#" className="btn btn-gray rounded-pill w-100"><Image src='/img/facebook.png' className="img-fluid me-2" width={20} height={20} alt="Facebook Signup"/>Signup with Facebook</Link>
                                    <Link href="#" className="btn btn-gray rounded-pill w-100"><Image src='/img/google.png' className="img-fluid me-2" width={20} height={20} alt="Google Signup"/>Signup with Google</Link>
                                </div>
                            </div>
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
