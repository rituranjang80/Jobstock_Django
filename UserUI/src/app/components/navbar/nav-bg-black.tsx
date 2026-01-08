'use client'
import React, { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function NavBgBlack() {
    let [toggle, setToggle] = useState<boolean>(false);
    let [scroll,setScroll] = useState<boolean>(false);
    let [menu, setMenu] = useState<string>('');
    let [windowWidth, setWindowWidth] = useState<number>(0);

    const loction = usePathname();

    useEffect(() => {
        if (typeof window !== 'undefined') {
            // set initial values
            setWindowWidth(window.innerWidth);
            window.scrollTo(0, 0);
            setMenu(loction);

            const handlerScroll = () => {
                setScroll(window.scrollY > 50);
            };

            const handleResize = () => {
                setWindowWidth(window.innerWidth);
            };

            window.addEventListener('scroll', handlerScroll);
            window.addEventListener('resize', handleResize);

            return () => {
                window.removeEventListener('scroll', handlerScroll);
                window.removeEventListener('resize', handleResize);
            };
        }
    }, [loction]);

  return (
    <>
        <div className={`header header-dark ${scroll ? 'header-fixed' : ''}`}>
            <div className="container">
                <nav id="navigation" className={windowWidth > 991 ? "navigation navigation-landscape" : "navigation navigation-portrait"}>
                    <div className="nav-header">
                        <Link className="nav-brand" href="#"><img src='/img/logo-light.png' className="logo" alt=""/></Link>
                        <div className="nav-toggle" onClick={()=>setToggle(!toggle)}></div>
                        <div className="mobile_nav">
                            <ul>
                                <li className="list-buttons">
                                    <Link href="#" data-bs-toggle="modal" data-bs-target="#login">
                                        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                            <path opacity="0.3" d="M22 12C22 17.5 17.5 22 12 22C6.5 22 2 17.5 2 12C2 6.5 6.5 2 12 2C17.5 2 22 6.5 22 12ZM12 7C10.3 7 9 8.3 9 10C9 11.7 10.3 13 12 13C13.7 13 15 11.7 15 10C15 8.3 13.7 7 12 7Z" className="fill-main"/>
                                            <path d="M12 22C14.6 22 17 21 18.7 19.4C17.9 16.9 15.2 15 12 15C8.8 15 6.09999 16.9 5.29999 19.4C6.99999 21 9.4 22 12 22Z" className="fill-main"/>
                                        </svg>
                                    </Link>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <div className={`nav-menus-wrapper ${toggle ? 'nav-menus-wrapper-open' : ''}`}>
                        <span className="nav-menus-wrapper-close-button" onClick={()=>setToggle(!toggle)}>✕</span>
                        <ul className="nav-menu">
                        
                            <li className={`nav-submenu-open ${['/','/home-2','/home-3','/home-4','/home-5','/home-6','/home-7','/home-8','/home-9','/home-10','/home-11','/home-12'].includes(menu) ? 'active' : ''}`}><Link href="#">Home<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                <ul className="nav-dropdown nav-submenu">
                                    <li className={`${menu === '/' ? 'active' : ''}`}><Link href="/">Home Layout 1</Link></li>
                                    <li className={`${menu === '/home-2' ? 'active' : ''}`}><Link href="/home-2">Home Layout 2</Link></li>
                                    <li className={`${menu === '/home-3' ? 'active' : ''}`}><Link href="/home-3">Home Layout 3</Link></li>
                                    <li className={`${menu === '/home-4' ? 'active' : ''}`}><Link href="/home-4">Home Layout 4</Link></li>
                                    <li className={`${menu === '/home-5' ? 'active' : ''}`}><Link href="/home-5">Home Layout 5</Link></li>
                                    <li className={`${menu === '/home-6' ? 'active' : ''}`}><Link href="/home-6">Home Layout 6</Link></li>
                                    <li className={`${menu === '/home-7' ? 'active' : ''}`}><Link href="/home-7">Home Layout 7</Link></li>
                                    <li className={`${menu === '/home-8' ? 'active' : ''}`}><Link href="/home-8">Home Layout 8</Link></li>                                    
                                    <li className={`${menu === '/home-9' ? 'active' : ''}`}><Link href="/home-9">Home Layout 9</Link></li>                                    
                                    <li className={`${menu === '/home-10' ? 'active' : ''}`}><Link href="/home-10">Home Layout 10</Link></li>
                                    <li className={`${menu === '/home-11' ? 'active' : ''}`}><Link href="/home-11">Home Layout 11</Link></li>
                                    <li className={`${menu === '/home-12' ? 'active' : ''}`}><Link href="/home-12">Home Layout 12</Link></li>	
                                </ul>
                            </li>
                            
                            <li className={`nav-submenu-open ${['/grid-style-1','/grid-style-2','/grid-style-3','/grid-style-4','/grid-style-5','/full-job-grid-1','/full-job-grid-2','/list-style-1','/list-style-2','/list-style-3','/full-job-list-1','/full-job-list-2','/half-map','/half-map-2','/half-map-3','/half-map-list-1','/half-map-list-2','/candidate-grid-1','/candidate-grid-2','/candidate-list-1','/candidate-list-2','/candidate-half-map','/candidate-half-map-list','/single-layout-1','/single-layout-2','/single-layout-3','/single-layout-4','/job-detail','/single-layout-6','/candidate-detail','/candidate-detail-2','/candidate-detail-3','/advance-search','/candidate-dashboard'].includes(menu) ? 'active' : ''}`}><Link href="#">For Candidate<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                <ul className="nav-dropdown nav-submenu">
                                    <li className={`nav-submenu-open ${['/grid-style-1','/grid-style-2','/grid-style-3','/grid-style-4','/grid-style-5','/full-job-grid-1','/full-job-grid-2','/list-style-1','/list-style-2','/list-style-3','/full-job-list-1','/full-job-list-2'].includes(menu) ? 'active' : ''}`}><Link href="#">Browse Jobs<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                        <ul className="nav-dropdown nav-submenu">
                                            <li className={`${menu === '/grid-style-1' ? 'active' : ''}`}><Link href="/grid-style-1">Job Grid Style 1</Link></li>                                    
                                            <li className={`${menu === '/grid-style-2' ? 'active' : ''}`}><Link href="/grid-style-2">Job Grid Stle 2</Link></li>                                    
                                            <li className={`${menu === '/grid-style-3' ? 'active' : ''}`}><Link href="/grid-style-3">Job Grid Style 3</Link></li>
                                            <li className={`${menu === '/grid-style-4' ? 'active' : ''}`}><Link href="/grid-style-4">Job Grid Style 4</Link></li>
                                            <li className={`${menu === '/grid-style-5' ? 'active' : ''}`}><Link href="/grid-style-5">Job Grid Style 5</Link></li>												
                                            <li className={`${menu === '/full-job-grid-1' ? 'active' : ''}`}><Link href="/full-job-grid-1">Grid Full Style 1</Link></li>
                                            <li className={`${menu === '/full-job-grid-2' ? 'active' : ''}`}><Link href="/full-job-grid-2">Grid Full Style 2</Link></li>
                                            <li className={`${menu === '/list-style-1' ? 'active' : ''}`}><Link href="/list-style-1">Job List Style 1</Link></li>
                                            <li className={`${menu === '/list-style-2' ? 'active' : ''}`}><Link href="/list-style-2">Job List Style 2</Link></li>
                                            <li className={`${menu === '/list-style-3' ? 'active' : ''}`}><Link href="/list-style-3">Job List Style 3</Link></li>
                                            <li className={`${menu === '/full-job-list-1' ? 'active' : ''}`}><Link href="/full-job-list-1">List Full Style 1</Link></li>
                                            <li className={`${menu === '/full-job-list-2' ? 'active' : ''}`}><Link href="/full-job-list-2">List Full Style 2</Link></li>												
                                        </ul>
                                    </li>
                                    <li className={`nav-submenu-open ${['/half-map','/half-map-2','/half-map-3','/half-map-list-1','/half-map-list-2'].includes(menu) ? 'active' : ''}`}><Link href="#">Browse Map Jobs<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                        <ul className="nav-dropdown nav-submenu">
                                            <li className={`${menu === '/half-map' ? 'active' : ''}`}><Link href="/half-map">Job Search on Map 01</Link></li>                                    
                                            <li className={`${menu === '/half-map-2' ? 'active' : ''}`}><Link href="/half-map-2">Job Search on Map 02</Link></li>                                    
                                            <li className={`${menu === '/half-map-3' ? 'active' : ''}`}><Link href="/half-map-3">Job Search on Map 03</Link></li>
                                            <li className={`${menu === '/half-map-list-1' ? 'active' : ''}`}><Link href="/half-map-list-1">Job Search on Map 04</Link></li>
                                            <li className={`${menu === '/half-map-list-2' ? 'active' : ''}`}><Link href="/half-map-list-2">Job Search on Map 05</Link></li>
                                        </ul>
                                    </li>
                                    <li className={`nav-submenu-open ${['/candidate-grid-1','/candidate-grid-2','/candidate-list-1','/candidate-list-2','/candidate-half-map','/candidate-half-map-list'].includes(menu) ? 'active' : ''}`}><Link href="#">Browse Candidate<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                        <ul className="nav-dropdown nav-submenu">
                                            <li className={`${menu === '/candidate-grid-1' ? 'active' : ''}`}><Link href="/candidate-grid-1">Candidate Grid 01</Link></li>                                    
                                            <li className={`${menu === '/candidate-grid-2' ? 'active' : ''}`}><Link href="/candidate-grid-2">Candidate Grid 02</Link></li>                                    
                                            <li className={`${menu === '/candidate-list-1' ? 'active' : ''}`}><Link href="/candidate-list-1">Candidate List 01</Link></li>                                    
                                            <li className={`${menu === '/candidate-list-2' ? 'active' : ''}`}><Link href="/candidate-list-2">Candidate List 02</Link></li>
                                            <li className={`${menu === '/candidate-half-map' ? 'active' : ''}`}><Link href="/candidate-half-map">Candidate Half Map 01</Link></li>
                                            <li className={`${menu === '/candidate-half-map-list' ? 'active' : ''}`}><Link href="/candidate-half-map-list">Candidate Half Map 02</Link></li>												
                                        </ul>
                                    </li>
                                    <li className={`nav-submenu-open ${['/single-layout-1','/single-layout-2','/single-layout-3','/single-layout-4','/job-detail','/single-layout-6',].includes(menu) ? 'active' : ''}`}><Link href="#">Single job Detail<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                        <ul className="nav-dropdown nav-submenu">
                                            <li className={`${menu === '/single-layout-1' ? 'active' : ''}`}><Link href="/single-layout-1">Single Layout 01</Link></li>                                    
                                            <li className={`${menu === '/single-layout-2' ? 'active' : ''}`}><Link href="/single-layout-2">Single Layout 02</Link></li>                                    
                                            <li className={`${menu === '/single-layout-3' ? 'active' : ''}`}><Link href="/single-layout-3">Single Layout 03</Link></li>                                    
                                            <li className={`${menu === '/single-layout-4' ? 'active' : ''}`}><Link href="/single-layout-4">Single Layout 04</Link></li>												
                                            <li className={`${menu === '/job-detail' ? 'active' : ''}`}><Link href="/job-detail">Single Layout 05</Link></li>												
                                            <li className={`${menu === '/single-layout-6' ? 'active' : ''}`}><Link href="/single-layout-6">Single Layout 06</Link></li>												
                                        </ul>
                                    </li>
                                    <li className={`nav-submenu-open ${['/candidate-detail','/candidate-detail-2','/candidate-detail-3'].includes(menu) ? 'active' : ''}`}><Link href="#">Candidate Detail<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                        <ul className="nav-dropdown nav-submenu">
                                            <li className={`${menu === '/candidate-detail' ? 'active' : ''}`}><Link href="/candidate-detail">Candidate Detail 01</Link></li>                                    
                                            <li className={`${menu === '/candidate-detail-2' ? 'active' : ''}`}><Link href="/candidate-detail-2">Candidate Detail 02</Link></li>                                    
                                            <li className={`${menu === '/candidate-detail-3' ? 'active' : ''}`}><Link href="/candidate-detail-3">Candidate Detail 03</Link></li>                                    												
                                        </ul>
                                    </li>
                                    <li><Link href="/advance-search">Advance Search</Link></li>
                                    <li>
                                        <Link href="/candidate-dashboard">Candidate Dashboard</Link>                                
                                    </li>
                                </ul>
                            </li>
                            
                            <li className={`nav-submenu-open ${['/employer-grid-1','/employer-grid-2','/employer-list-1','/employer-half-map','/employer-half-map-list','/employer-detail','/employer-detail-2','/employer-dashboard'].includes(menu) ? 'active' : ''}`}><Link href="#">For Employer<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                <ul className="nav-dropdown nav-submenu">
                                    <li className={`nav-submenu-open ${['/employer-grid-1','/employer-grid-2','/employer-list-1','/employer-half-map','/employer-half-map-list'].includes(menu) ? 'active' : ''}`}><Link href="#">Explore Employers<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                        <ul className="nav-dropdown nav-submenu">
                                            <li className={`${menu === '/employer-grid-1' ? 'active' : ''}`}><Link href="/employer-grid-1">Search Employers 01</Link></li>                                    
                                            <li className={`${menu === '/employer-grid-2' ? 'active' : ''}`}><Link href="/employer-grid-2">Search Employers 02</Link></li>                                    
                                            <li className={`${menu === '/employer-list-1' ? 'active' : ''}`}><Link href="/employer-list-1">Search List Employers 01</Link></li>
                                            <li className={`${menu === '/employer-half-map' ? 'active' : ''}`}><Link href="/employer-half-map">Search Employers Map</Link></li>
                                            <li className={`${menu === '/employer-half-map-list' ? 'active' : ''}`}><Link href="/employer-half-map-list">Search List Employers Map</Link></li>												
                                        </ul>
                                    </li>
                                    <li className={`nav-submenu-open ${['/employer-detail','/employer-detail-2'].includes(menu) ? 'active' : ''}`}><Link href="#">Employer Detail<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                        <ul className="nav-dropdown nav-submenu">
                                            <li className={`${menu === '/employer-detail' ? 'active' : ''}`}><Link href="/employer-detail">Employer Detail 01</Link></li>                                    
                                            <li className={`${menu === '/employer-detail-2' ? 'active' : ''}`}><Link href="/employer-detail-2">Employer Detail 02</Link></li>                                    											
                                        </ul>
                                    </li>
                                    <li className={`${menu === '/employer-dashboard' ? 'active' : ''}`}><Link href="/employer-dashboard">Employer Dashboard</Link></li>
                                </ul>
                            </li>
                            
                            <li className={`nav-submenu-open ${['/about-us','/404','/checkout','/blog','/blog-detail','/privacy','/pricing','/faq','/contact'].includes(menu) ? 'active' : ''}`}><Link href="#">Pages<span className="submenu-indicator"><span className='submenu-indicator-chevron'></span></span></Link>
                                <ul className="nav-dropdown nav-submenu">
                                    <li className={`${menu === '/about-us' ? 'active' : ''}`}><Link href="/about-us">About Us</Link></li> 
                                    <li className={`${menu === '/404' ? 'active' : ''}`}><Link href="/404">Error Page</Link></li>
                                    <li className={`${menu === '/checkout' ? 'active' : ''}`}><Link href="/checkout">Checkout</Link></li>										
                                    <li className={`${menu === '/blog' ? 'active' : ''}`}><Link href="/blog">Blogs Page</Link></li>                                    
                                    <li className={`${menu === '/blog-detail' ? 'active' : ''}`}><Link href="/blog-detail">Blog Detail</Link></li>                                    
                                    <li className={`${menu === '/privacy' ? 'active' : ''}`}><Link href="/privacy">Terms & Privacy</Link></li> 
                                    <li className={`${menu === '/pricing' ? 'active' : ''}`}><Link href="/pricing">Pricing</Link></li>  
                                    <li className={`${menu === '/faq' ? 'active' : ''}`}><Link href="/faq">FAQ's</Link></li>
                                    <li className={`${menu === '/contact' ? 'active' : ''}`}><Link href="/contact">Contacts</Link></li>
                                </ul>
                            </li>
                            
                            <li className={`${menu === '/help' ? 'active' : ''}`}><Link href="/help">Help</Link></li>
                            
                        </ul>
                        
                        <ul className="nav-menu nav-menu-social align-to-right">
                            <li>
                                <Link href="#" data-bs-toggle="modal" data-bs-target="#login"><i className="fas fa-sign-in-alt me-2"></i>Sign In</Link>
                            </li>
                            <li className="list-buttons ms-2">
                                <Link href="/signup"><i className="bi bi-person-circle me-2"></i>Register Today</Link>
                            </li>
                        </ul>
                    </div>
                </nav>
            </div>
        </div>  

         <div className="modal fade" id="login" tabIndex={-1} role="dialog" aria-labelledby="loginmodal" aria-hidden="true">
				<div className="modal-dialog modal-dialog-centered login-pop-form" role="document">
					<div className="modal-content" id="loginmodal">
						<span className="mod-close" data-bs-dismiss="modal" aria-hidden="true"><i className="fas fa-close"></i></span>
						<div className="modal-header">
							<div className="mdl-thumb"><img src='/img/ico.png' className="img-fluid" width="70" alt=""/></div>
							<div className="mdl-title"><h4 className="modal-header-title">Hello, Again</h4></div>
						</div>
						<div className="modal-body">
							<div className="modal-login-form">
								<form>
								
									<div className="form-floating mb-4">
										<input type="email" className="form-control" placeholder="name@example.com"/>
										<label>User Name</label>
									</div>
									
									<div className="form-floating mb-4">
										<input type="password" className="form-control" placeholder="Password"/>
										<label>Password</label>
									</div>
									
									<div className="form-group">
										<button type="submit" className="btn btn-main full-width font--bold btn-lg">Log In</button>
									</div>
									
									<div className="modal-flex-item mb-3">
										<div className="modal-flex-first">
											<div className="form-check form-check-inline">
												<input className="form-check-input" type="checkbox" id="savepassword" value="option1"/>
												<label className="form-check-label" htmlFor="savepassword">Save Password</label>
											</div>
										</div>
										<div className="modal-flex-last">
											<Link href="#">Forget Password?</Link>
										</div>
									</div>
								</form>
							</div>
							<div className="social-login">
								<ul>
									<li><Link href="#" className="btn connect-fb"><i className="fa-brands fa-facebook"></i>Facebook</Link></li>
									<li><Link href="#" className="btn connect-google"><i className="fa-brands fa-google"></i>Google+</Link></li>
								</ul>
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
