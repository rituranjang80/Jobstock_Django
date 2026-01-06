'use client'
import React, { use } from 'react'
import Link from 'next/link'

import NavBgWhite from '../../components/navbar/nav-bg-white'
import FooterTopTwo from '../../components/footer/footer-top-two'
import FooterLightTwo from '../../components/footer/footer-light-two'
import ScrollToTop from '../../components/scroll-to-top'

import { jobData, requirements, responsibilities } from '../../data/data'
import Image from 'next/image'

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

export default function JobDetail({params}:{params:any}) {
    const { id }:any = use(params)

    let data:any = jobData.find((item)=>item.id === parseInt(id))
  return (
    <>
        <NavBgWhite/>

        <section className="bg-cover bg-second position-relative py-4">
            <div className="position-absolute end-0 top-0 bottom-0 d-lg-block d-none"><img src='/img/banner-1.jpg' className="img-fluid rounded-start-pill h-100" alt=""/></div>
            <div className="container">
                <div className="row">
                    <div className="col-xl-6 col-lg-9 col-md-12">
                        <div className="bread-wraps breadcrumbs light">
                            <nav aria-label="breadcrumb">
                                <ol className="breadcrumb">
                                    <li className="breadcrumb-item"><Link href="/">Home</Link></li>
                                    <li className="breadcrumb-item"><Link href="/grid-style-1">Career</Link></li>
                                    <li className="breadcrumb-item active" aria-current="page">{data && data.title}</li>
                                </ol>
                            </nav>
                        </div>
                        
                        <div className="jbs-head-bodys-top my-5">
                            <div className="jbs-roots-y1 flex-column justify-content-start align-items-start">
                                <div className="jbs-roots-y1-last">
                                    <div className="jbs-urt mb-2"><span className="label text-secondcolor bg-white rounded-pill">{data && data.jobtype}</span></div>
                                    <div className="jbs-title-iop mb-1"><h2 className="m-0 fs-2 text-light">{data && data.title}</h2></div>
                                    <div className="jbs-locat-oiu text-sm-muted text-light d-flex align-items-center">
                                        <span><i className="fa-solid fa-location-dot opacity-75 me-1"></i>{data && data.location}</span>
                                        <div className="jbs-kioyer-groups ms-3">
                                            <span className="fa-solid fa-star active"></span>
                                            <span className="fa-solid fa-star active"></span>
                                            <span className="fa-solid fa-star active"></span>
                                            <span className="fa-solid fa-star active"></span>
                                            <span className="fa-solid fa-star"></span>
                                            <span className="aal-reveis text-light opacity-75">4.6</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="jbs-roots-y6 py-3">
                                    <p className="text-light">We are looking for a experienced Senior Front-End Developer with an advanced level of english to design UI/UX interface for web and mobile apps.</p>
                                </div>
                                <div className="jbs-roots-y6 py-3">
                                    <button className="btn btn-main fw-medium px-lg-5 px-4 me-3" type="button" data-bs-toggle="modal" data-bs-target="#applyjob">Apply Job</button>
                                    <button className="btn btn-whites fw-medium px-lg-5 px-4" type="button">Save job</button>
                                </div>
                            </div>
                        </div>
                        
                        <div className="explot-info-details d-inline-flex flex-wrap">
                            <div className="single-explot d-flex align-items-center me-md-5 me-3 my-2">
                                <div className="single-explot-first">
                                    <i className="fa-solid fa-business-time text-main fs-1"></i>
                                </div>
                                <div className="single-explot-last ps-2">
                                    <span className="text-light opacity-75">Department</span>
                                    <p className="text-light fw-bold fs-6 m-0">Software</p>
                                </div>
                            </div>
                            <div className="single-explot d-flex align-items-center me-md-5 me-3 my-2">
                                <div className="single-explot-first">
                                    <i className="fa-solid fa-location-dot text-main fs-1"></i>
                                </div>
                                <div className="single-explot-last ps-2">
                                    <span className="text-light opacity-75">Location</span>
                                    <p className="text-light fw-bold fs-6 m-0">Canada, USA</p>
                                </div>
                            </div>
                            <div className="single-explot d-flex align-items-center">
                                <div className="single-explot-first">
                                    <i className="fa-solid fa-sack-dollar text-main fs-1"></i>
                                </div>
                                <div className="single-explot-last ps-2">
                                    <span className="text-light opacity-75">Sallary</span>
                                    <p className="text-light fw-bold fs-6 m-0">$5000-$10,000 PA</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>   

        <section className="gray-simple">
            <div className="container">
                <div className="row">
                    <div className="col-lg-8 col-md-12">
                        
                        <div className="jbs-blocs style_03 b-0 mb-md-4 mb-sm-4">
                            <div className="jbs-blocs-body px-4 py-4">
                                <div className="jbs-content mb-4">
                                    <h5>Job Description</h5>
                                    <p>Shreethemes Web provides equal employment opportunities to all qualified individuals without regard to race, color, religion, sex, gender identity, sexual orientation, pregnancy, age, national origin, physical or mental disability, military or veteran status, genetic information, or any other protected classification. Equal employment opportunity includes, but is not limited to, hiring, training, promotion, demotion, transfer, leaves of absence, and termination. Thynk Web takes allegations of discrimination, harassment, and retaliation seriously, and will promptly investigate when such behavior is reported.</p>
                                    <p>Our company is seeking to hire a skilled Web Developer to help with the development of our current projects. Your duties will primarily revolve around building software by writing code, as well as modifying software to fix errors, adapt it to new hardware, improve its performance, or upgrade interfaces. You will also be involved in directing system testing and validation procedures, and also working with customers or departments on technical issues including software system design and maintenance.</p>
                                    <p className="m-0">We are looking for a Senior Web Developer to build and maintain functional web pages and applications. Senior Web Developer will be leading junior developers, refining website specifications, and resolving technical issues. He/She should have extensive experience building web pages from scratch and in-depth knowledge of at least one of the following programming languages: Javascript, Ruby, or PHP. He/She will ensure our web pages are up and running and cover both internal and customer needs.</p>
                                </div>
                                <div className="jbs-content-body mb-4">
                                    <h5 className="mb-3">Job Requirements</h5>
                                    <div className="jbs-content mb-3">
                                        <h6>Requirements:</h6>
                                        <ul className="simple-list">
                                            {requirements.map((item:string,index:number)=>( 
                                                <li key={index}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                    
                                    <div className="jbs-content mb-4">
                                        <h6>Responsibilities:</h6>
                                        <ul className="simple-list">
                                            {responsibilities.map((item:string,index:number)=>( 
                                                <li key={index}>{item}</li>
                                            ))}
                                        </ul>
                                    </div>
                                    
                                    <div className="jbs-content">
                                        <h6>Qualifications and Skills</h6>
                                        <ul className="colored-list">
                                            <li>Bachelor's degree</li>
                                            <li>BCA/MCA</li>
                                            <li>BSC IT/Msc IT</li>
                                            <li>Or any other equivalent degree</li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                            <div className="jbs-blox-footer">
                                <div className="blox-first-footer">
                                    <div className="ftr-share-block">
                                        <ul>
                                            <li><strong>Share This Job:</strong></li>
                                            <li><Link href="#"><i className="fa-brands fa-facebook"></i></Link></li>
                                            <li><Link href="#"><i className="fa-brands fa-linkedin"></i></Link></li>
                                            <li><Link href="#"><i className="fa-brands fa-google-plus"></i></Link></li>
                                            <li><Link href="#"><i className="fa-brands fa-twitter"></i></Link></li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                    </div>
                    
                    <div className="col-lg-4 col-md-12">
                        <div className="detail-side-block bg-white mb-4">
                            <div className="detail-side-heads mb-2">
                                <h3>Ready To Apply?</h3>
                                <p>Complete the eligibities checklist now and get started with your online application</p>
                            </div>
                            <div className="detail-side-middle">
                                <div className="form-floating mb-3">
                                    <input type="text" className="form-control" placeholder=""/>
                                    <label>Name:</label>
                                </div>
                                <div className="form-floating mb-3">
                                    <input type="text" className="form-control" placeholder=""/>
                                    <label>Email:</label>
                                </div>
                                <div className="form-group">
                                    <div className="upload-btn-wrapper full-width">
                                        <button className="btn full-width">Upload Resume</button>
                                        <input type="file" name="myfile"/>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <div className="elsoci"><label>Are you authorised to work in India?</label></div>
                                    <div className="form-check form-check-inline">
                                        <input className="form-check-input" type="radio" name="workindia" id="wyes" value="option1"/>
                                        <label className="form-check-label" htmlFor="wyes">Yes</label>
                                    </div>
                                    <div className="form-check form-check-inline">
                                        <input className="form-check-input" type="radio" name="workindia" id="wno" value="option1"/>
                                        <label className="form-check-label" htmlFor="wno">No</label>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <div className="elsoci"><label>Do you have master degree?</label></div>
                                    <div className="form-check form-check-inline">
                                        <input className="form-check-input" type="radio" name="degree" id="dyed" value="option1"/>
                                        <label className="form-check-label" htmlFor="dyed">Yes</label>
                                    </div>
                                    <div className="form-check form-check-inline">
                                        <input className="form-check-input" type="radio" name="degree" id="dno" value="option1"/>
                                        <label className="form-check-label" htmlFor="dno">No</label>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <div className="form-check form-check-inline">
                                        <input className="form-check-input" type="checkbox" id="jobalert" value="option1"/>
                                        <label className="form-check-label" htmlFor="jobalert">Create Job Alert</label>
                                    </div>
                                </div>
                                <div className="form-group">
                                    <button type="button" className="btn btn-main full-width fw-medium font-sm">Submit Application</button>
                                </div>
                            </div>
                        </div>
                        
                        <div className="side-jbs-info-blox bg-white mb-4">
                            <div className="side-jbs-info-header">
                                <div className="side-jbs-info-thumbs">
                                    <figure><Image src={data && data.image} width={70} height={70} className="img-fluid" alt=""/></figure>
                                </div>
                                <div className="side-jbs-info-captionyo ps-3">
                                    <div className="sld-info-title">
                                        <h5 className="rtls-title mb-1">{data && data.name} Inc.</h5>
                                        <div className="jbs-locat-oiu text-sm-muted">
                                            <span className="me-1"><i className="fa-solid fa-location-dot me-1"></i>{data && data.location}</span>.<span className="ms-1">Software & Consultancy</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="side-jbs-info-middle">
                                <div className="side-full-info-groups">
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Company Founder:</span>
                                        <h6 className="sld-title">Mr. Daniel Mark</h6>
                                    </div>
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Industry:</span>
                                        <h6 className="sld-title">Technology</h6>
                                    </div>
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Founded:</span>
                                        <h6 className="sld-title">1997</h6>
                                    </div>
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Head Office:</span>
                                        <h6 className="sld-title">{data && data.location}</h6>
                                    </div>
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Revenue</span>
                                        <h6 className="sld-title">$70B+</h6>
                                    </div>
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Company Size:</span>
                                        <h6 className="sld-title">20,000+ Emp.</h6>
                                    </div>
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Min Exp.</span>
                                        <h6 className="sld-title">02 Years</h6>
                                    </div>
                                    <div className="single-side-info">
                                        <span className="text-sm-muted sld-subtitle">Openings</span>
                                        <h6 className="sld-title">06 Openings</h6>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div className="side-rtl-jbs-block bg-white ">
                            <div className="side-rtl-jbs-head">
                                <h5 className="side-jbs-titles">Related Jobs</h5>
                            </div>
                            <div className="side-rtl-jbs-body">
                                <div className="side-rtl-jbs-groups">

                                    {jobData.slice(0,5).map((item:JobData,index:number)=>( 
                                        <div className="single-side-rtl-jbs" key={index}>
                                            <div className="single-fliox">
                                                <div className="single-rtl-jbs-thumb">
                                                    <Link href={`/job-detail/${item.id}`}><figure><Image src={item.image} width={70} height={70} className="img-fluid" alt=""/></figure></Link>
                                                </div>
                                                <div className="single-rtl-jbs-caption ms-2">
                                                    <div className="hjs-rtls-titles">
                                                        <div className="jbs-types mb-1">
                                                            {item.jobtype === 'Enternship' && <span className="label text-danger bg-danger bg-opacity-05">Enternship</span>}
                                                            {item.jobtype === 'Freelancer' && <span className="label text-info bg-info bg-opacity-05">Freelancer</span>}
                                                            {item.jobtype === 'Part Time' && <span className="label text-warning bg-warning bg-opacity-05">Part Time</span>}
                                                            {item.jobtype === 'Full Time' && <span className="label text-success bg-success bg-opacity-05">Full Time</span>}
                                                        </div>
                                                        <h5 className="rtls-title py-2"><Link href={`/job-detail/${item.id}`}>{item.title}</Link></h5>
                                                        <div className="jbs-locat-oiu text-sm-muted">
                                                            <span><i className="fa-solid fa-location-dot me-1"></i>{item.location}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="single-rtl-jbs-hot">
                                                <div className="single-tag-rtls"><span className="label text-warning bg-warning bg-opacity-05"><i className="fa-brands fa-hotjar me-1"></i>New</span></div>
                                                <div className="single-tag-rtls"><span className="label text-success bg-success bg-opacity-05"><i className="fa-solid fa-star me-1"></i>Featured</span></div>
                                            </div>
                                        </div>
                                    ))}
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

        <div className="modal fade" id="applyjob" tabIndex={-1} role="dialog" aria-labelledby="applyjobs" aria-hidden="true">
            <div className="modal-dialog modal-dialog-centered applyjob-pop-form" role="document">
                <div className="modal-content" id="applyjobs">
                    <span className="mod-close" data-bs-dismiss="modal" aria-hidden="true"><i className="fas fa-close"></i></span>
                    <div className="modal-body">
                        <div className="detail-side-heads mb-4 mt-4">
                            <h3>Ready To Apply?</h3>
                            <p>Complete the eligibities checklist now and get started with your online application</p>
                        </div>
                        <div className="detail-side-middle">
                            <div className="form-floating mb-3">
                                <input type="text" className="form-control" placeholder=""/>
                                <label>Name:</label>
                            </div>
                            <div className="form-floating mb-3">
                                <input type="text" className="form-control" placeholder=""/>
                                <label>Email:</label>
                            </div>
                            <div className="form-group">
                                <div className="upload-btn-wrapper full-width">
                                    <button className="btn full-width">Upload Resume</button>
                                    <input type="file" name="myfile"/>
                                </div>
                            </div>
                            <div className="form-group">
                                <div className="elsoci"><label>Are you authorised to work in India?</label></div>
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="radio" name="workindia" id="wyes" value="option1"/>
                                    <label className="form-check-label" htmlFor="wyes">Yes</label>
                                </div>
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="radio" name="workindia" id="wno" value="option1"/>
                                    <label className="form-check-label" htmlFor="wno">No</label>
                                </div>
                            </div>
                            <div className="form-group">
                                <div className="elsoci"><label>Do you have master degree?</label></div>
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="radio" name="degree" id="dyed" value="option1"/>
                                    <label className="form-check-label" htmlFor="dyed">Yes</label>
                                </div>
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="radio" name="degree" id="dno" value="option1"/>
                                    <label className="form-check-label" htmlFor="dno">No</label>
                                </div>
                            </div>
                            <div className="form-group">
                                <div className="form-check form-check-inline">
                                    <input className="form-check-input" type="checkbox" id="jobalert" value="option1"/>
                                    <label className="form-check-label" htmlFor="jobalert">Create Job Alert</label>
                                </div>
                            </div>
                            <div className="form-group">
                                <button type="button" className="btn btn-main full-width fw-medium font-sm">Submit Application</button>
                            </div>
                        </div>
                    </div>
                    <div className="modal-footer">
                        <p>Don't have an account yet?<Link href="/signup" className="text-main font--bold ms-1">Sign Up</Link></p>
                    </div>
                </div>
            </div>
        </div>
    </>
  )
}
